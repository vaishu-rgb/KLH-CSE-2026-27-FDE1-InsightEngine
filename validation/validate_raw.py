"""
InsightEngine — Validation & Preprocessing.

Reads raw tables from Postgres, applies validation rules,
writes clean + rejected CSVs to data/processed/, and logs
results to raw.validation_metadata.

Usage:
    python -m validation.validate_raw
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from validation.rules import (
    ALLOWED_SEGMENTS, ALLOWED_ORDER_STATUSES, ALLOWED_PAYMENT_STATUSES,
    ALLOWED_CATEGORIES, COLUMN_TYPES, FOREIGN_KEYS, TABLE_ORDER, RULES
)

# ---------- Paths + env ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_DB_HOST = os.getenv("RAW_DB_HOST", "127.0.0.1")
RAW_DB_PORT = os.getenv("POSTGRES_RAW_PORT", "5432")
RAW_DB_USER = os.getenv("POSTGRES_RAW_USER", "raw_user")
RAW_DB_PASS = os.getenv("POSTGRES_RAW_PASSWORD", "raw_pass")
RAW_DB_NAME = os.getenv("POSTGRES_RAW_DB", "insightengine_raw")

RAW_DB_URL = (
    f"postgresql+psycopg2://{RAW_DB_USER}:{RAW_DB_PASS}"
    f"@{RAW_DB_HOST}:{RAW_DB_PORT}/{RAW_DB_NAME}"
)


# ============================================================
# Type coercion
# ============================================================
def coerce_types(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """Convert TEXT columns to proper types. Bad values become NaN/NaT."""
    type_map = COLUMN_TYPES.get(table, {})
    for col, target in type_map.items():
        if col not in df.columns:
            continue
        if target == "int":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif target == "float":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif target == "date":
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        elif target == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


# ============================================================
# Referential integrity
# ============================================================
def load_fk_reference(engine, ref_table: str, ref_col: str) -> set:
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT {ref_col} FROM raw.{ref_table}")).fetchall()
    return {r[0] for r in rows}


# ============================================================
# Validation per table
# ============================================================
def validate_table(engine, table: str, fk_cache: dict):
    """
    Returns (clean_df, rejected_df, stats_dict).
    rejected_df has extra column: rejection_reason.
    """
    print(f"\n[{table}] reading raw...")
    df = pd.read_sql(f"SELECT * FROM raw.{table}", engine)
    total = len(df)

    # ---- Type coercion first ----
    df = coerce_types(df, table)

    # ---- Build rejection mask ----
    reject_mask = pd.Series(False, index=df.index)
    reject_reasons = pd.Series("", index=df.index)

    def reject(mask: pd.Series, reason: str):
        nonlocal reject_mask, reject_reasons
        newly = mask & ~reject_mask
        reject_reasons.loc[newly] = reason
        reject_mask = reject_mask | mask

    # ---------- Table-specific rules ----------
    if table == "customers":
        # duplicate customer_id
        dup = df.duplicated(subset=["customer_id"], keep="first")
        reject(dup, "duplicate customer_id")
        # fix bad segment
        bad_seg = ~df["segment"].isin(ALLOWED_SEGMENTS) & df["segment"].notna()
        df.loc[bad_seg, "segment"] = "unknown"

    elif table == "products":
        reject(df["price"].isna() | (df["price"] <= 0), "price <= 0 or invalid")
        reject(df["category"].isna() | ~df["category"].isin(ALLOWED_CATEGORIES),
               "invalid or missing category")

    elif table == "orders":
        reject(df.duplicated(subset=["order_id"], keep="first"), "duplicate order_id")
        cust_ids = fk_cache["customers"]
        reject(~df["customer_id"].isin(cust_ids), "customer_id not in customers")
        reject(df["total_amount"].isna() | (df["total_amount"] <= 0),
               "total_amount <= 0 or invalid")
        bad_status = ~df["status"].isin(ALLOWED_ORDER_STATUSES) & df["status"].notna()
        df.loc[bad_status, "status"] = "unknown"

    elif table == "order_items":
        reject(df["quantity"].isna() | (df["quantity"] <= 0),
               "quantity <= 0 or invalid")
        reject(~df["order_id"].isin(fk_cache["orders"]), "order_id not in orders")
        reject(~df["product_id"].isin(fk_cache["products"]),
               "product_id not in products")

    elif table == "payments":
        reject(~df["status"].isin(ALLOWED_PAYMENT_STATUSES),
               "invalid payment status")
        reject(~df["order_id"].isin(fk_cache["orders"]), "order_id not in orders")
        reject(df["amount"].isna() | (df["amount"] <= 0), "amount <= 0 or invalid")

    elif table == "inventory":
        bad_qty = df["quantity_on_hand"].isna() | (df["quantity_on_hand"] < 0)
        df.loc[bad_qty, "quantity_on_hand"] = 0
        bad_reorder = df["reorder_level"].isna() | (df["reorder_level"] <= 0)
        df.loc[bad_reorder, "reorder_level"] = 10

    # ---------- Split ----------
    clean = df[~reject_mask].copy()
    rejected = df[reject_mask].copy()
    if not rejected.empty:
        rejected["rejection_reason"] = reject_reasons[reject_mask]

    stats = {
        "table": table,
        "total": total,
        "clean": len(clean),
        "rejected": len(rejected),
    }
    return clean, rejected, stats


# ============================================================
# Logging
# ============================================================
def ensure_validation_log_table(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw.validation_metadata (
                id SERIAL PRIMARY KEY,
                table_name TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                clean_rows INTEGER NOT NULL,
                rejected_rows INTEGER NOT NULL,
                validated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))


def log_validation(engine, stats: dict):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO raw.validation_metadata
                (table_name, total_rows, clean_rows, rejected_rows)
                VALUES (:t, :tot, :c, :r)
            """),
            {"t": stats["table"], "tot": stats["total"],
             "c": stats["clean"], "r": stats["rejected"]},
        )


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("InsightEngine — Validation & Preprocessing")
    print("=" * 60)

    engine = create_engine(RAW_DB_URL, future=True)
    ensure_validation_log_table(engine)

    fk_cache = {}
    all_stats = []

    for table in TABLE_ORDER:
        clean, rejected, stats = validate_table(engine, table, fk_cache)

        # write CSVs
        clean_path = PROCESSED_DIR / f"{table}_clean.csv"
        rejected_path = PROCESSED_DIR / f"{table}_rejected.csv"
        clean.to_csv(clean_path, index=False)
        if not rejected.empty:
            rejected.to_csv(rejected_path, index=False)
        elif rejected_path.exists():
            rejected_path.unlink()

        log_validation(engine, stats)
        all_stats.append(stats)

        print(f"[{table}] total={stats['total']:,}  "
              f"clean={stats['clean']:,}  rejected={stats['rejected']:,}")

        # cache PKs for downstream FK checks
        if table == "customers":
            fk_cache["customers"] = set(clean["customer_id"])
        elif table == "products":
            fk_cache["products"] = set(clean["product_id"])
        elif table == "orders":
            fk_cache["orders"] = set(clean["order_id"])

    # ---- summary ----
    print("\n" + "=" * 60)
    print("Validation summary")
    print("=" * 60)
    total_in = sum(s["total"] for s in all_stats)
    total_clean = sum(s["clean"] for s in all_stats)
    total_rej = sum(s["rejected"] for s in all_stats)
    pct = 100.0 * total_rej / total_in if total_in else 0.0
    print(f"  total rows in     : {total_in:>10,}")
    print(f"  clean rows out    : {total_clean:>10,}")
    print(f"  rejected rows     : {total_rej:>10,}  ({pct:.2f}%)")
    print(f"\n✅ Validation complete. Clean CSVs in: {PROCESSED_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1)