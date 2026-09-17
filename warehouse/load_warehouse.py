"""
InsightEngine — Load star schema warehouse from Spark Parquet.

Reads Parquet files from data/processed/spark/, populates the warehouse
Postgres (insightengine_dw) with dimension + fact tables.

Usage:
    python -m warehouse.load_warehouse
"""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------- Paths + env ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SPARK_DIR = PROJECT_ROOT / "data" / "processed" / "spark"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"

DW_DB_HOST = os.getenv("DW_DB_HOST", "127.0.0.1")
DW_DB_PORT = os.getenv("POSTGRES_DW_PORT", "5433")
DW_DB_USER = os.getenv("POSTGRES_DW_USER", "dw_user")
DW_DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "dw_pass")
DW_DB_NAME = os.getenv("POSTGRES_DW_DB", "insightengine_dw")

DW_DB_URL = (
    f"postgresql+psycopg2://{DW_DB_USER}:{DW_DB_PASS}"
    f"@{DW_DB_HOST}:{DW_DB_PORT}/{DW_DB_NAME}"
)


# ============================================================
# Helpers
# ============================================================
def read_parquet(name: str) -> pd.DataFrame:
    path = SPARK_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"missing parquet: {path}")
    return pd.read_parquet(path)


def pg_copy(engine, table: str, df: pd.DataFrame):
    """Fast bulk load via PostgreSQL COPY."""
    import io
    if df.empty:
        print(f"  [skip] {table}: 0 rows")
        return
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute(f"TRUNCATE warehouse.{table} CASCADE;")
        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False, na_rep="\\N")
        buf.seek(0)
        cols = ", ".join(df.columns)
        cur.copy_expert(
            f"COPY warehouse.{table} ({cols}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')",
            buf,
        )
        raw.commit()
        print(f"  [load] {table:<22} {len(df):>8,} rows")
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


# ============================================================
# Date dimension
# ============================================================
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def build_dim_date(start: date, end: date) -> pd.DataFrame:
    rows = []
    d = start
    while d <= end:
        dow = (d.weekday() + 1) % 7  # 0=Sun..6=Sat  -> shift to our key space
        # Python weekday(): Mon=0..Sun=6.  We want 1=Sun..7=Sat
        py_dow = d.weekday()          # Mon=0..Sun=6
        our_dow = ((py_dow + 1) % 7) + 1  # Sun=1..Sat=7
        rows.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "full_date": d.isoformat(),
            "year": d.year,
            "quarter": (d.month - 1) // 3 + 1,
            "month": d.month,
            "month_name": MONTH_NAMES[d.month - 1],
            "day_of_month": d.day,
            "day_of_week": our_dow,
            "day_name": DAY_NAMES[our_dow - 1],
            "is_weekend": our_dow in (1, 7),
            "week_of_year": int(d.strftime("%U")),
        })
        d += timedelta(days=1)
    return pd.DataFrame(rows)


# ============================================================
# Main loader
# ============================================================
def main():
    print("=" * 60)
    print("InsightEngine — Load Star Schema Warehouse")
    print("=" * 60)
    print(f"[conn] {DW_DB_URL.replace(DW_DB_PASS, '****')}\n")

    engine = create_engine(DW_DB_URL, future=True)

    # ---- Apply schema ----
    print(f"[schema] applying {SCHEMA_FILE.name}")
    ddl = SCHEMA_FILE.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("[schema] warehouse schema created\n")

    # ---- Read all parquet ----
    print("[read] loading parquet datasets...")
    customers_df   = read_parquet("customers")
    products_df    = read_parquet("products")
    orders_df      = read_parquet("orders")
    order_items_df = read_parquet("order_items")
    payments_df    = read_parquet("payments")
    inventory_df   = read_parquet("inventory")
    print(f"  customers={len(customers_df):,}  products={len(products_df):,}  "
          f"orders={len(orders_df):,}  items={len(order_items_df):,}  "
          f"payments={len(payments_df):,}  inventory={len(inventory_df):,}\n")

    # ============================================================
    # 1. DIM: customers
    # ============================================================
    print("[dim] customers")
    cust_dim = customers_df[[
        "customer_id", "full_name", "email", "phone", "city", "country",
        "segment", "signup_date", "signup_year", "signup_month", "tenure_days"
    ]].copy()
    cust_dim["signup_date"] = pd.to_datetime(cust_dim["signup_date"]).dt.date
    pg_copy(engine, "dim_customers", cust_dim)

    # ============================================================
    # 2. DIM: products
    # ============================================================
    print("[dim] products")
    prod_dim = products_df[[
        "product_id", "product_name", "category", "brand",
        "price", "cost", "margin_amount", "margin_pct",
        "price_band", "created_at"
    ]].copy()
    prod_dim["created_at"] = pd.to_datetime(prod_dim["created_at"]).dt.date
    pg_copy(engine, "dim_products", prod_dim)

    # ============================================================
    # 3. DIM: payments
    # ============================================================
    print("[dim] payments")
    pay_dim = payments_df[[
        "payment_id", "order_id", "method", "status", "is_success",
        "payment_delay_hours", "amount", "currency"
    ]].copy()
    # bucket delay
    def delay_bucket(h):
        if pd.isna(h):
            return "unknown"
        if h < 1:
            return "instant"
        if h < 24:
            return "same_day"
        if h < 72:
            return "within_3_days"
        return "delayed"
    pay_dim["delay_bucket"] = pay_dim["payment_delay_hours"].apply(delay_bucket)
    pg_copy(engine, "dim_payments", pay_dim)

    # ============================================================
    # 4. DIM: inventory
    # ============================================================
    print("[dim] inventory")
    inv_dim = inventory_df[[
        "inventory_id", "product_id", "warehouse", "quantity_on_hand",
        "reorder_level", "stock_status", "needs_reorder", "last_updated"
    ]].copy()
    pg_copy(engine, "dim_inventory", inv_dim)

    # ============================================================
    # 5. DIM: date (generated from actual order range)
    # ============================================================
    print("[dim] date")
    order_dates = pd.to_datetime(orders_df["order_date"])
    start = order_dates.min().date() - timedelta(days=30)
    end   = order_dates.max().date() + timedelta(days=30)
    date_dim = build_dim_date(start, end)
    pg_copy(engine, "dim_date", date_dim)

    # ============================================================
    # 6. FACT: orders
    # ============================================================
    print("[fact] orders")
    # Pull surrogate keys from DB
    with engine.connect() as conn:
        cust_map = dict(conn.execute(text(
            "SELECT customer_id, customer_key FROM warehouse.dim_customers"
        )).fetchall())
        order_dates = order_dates  # already datetime

    fact_orders = orders_df[[
        "order_id", "customer_id", "order_date", "order_timestamp",
        "status", "total_amount", "currency", "order_hour", "is_weekend"
    ]].copy()

    fact_orders["customer_key"] = fact_orders["customer_id"].map(cust_map).astype("Int64")
    fact_orders["order_timestamp"] = pd.to_datetime(fact_orders["order_timestamp"])
    fact_orders["date_key"] = (
        pd.to_datetime(fact_orders["order_date"]).dt.strftime("%Y%m%d").astype(int)
    )
    fact_orders = fact_orders[[
        "order_id", "customer_key", "date_key", "order_timestamp",
        "status", "total_amount", "currency", "order_hour", "is_weekend"
    ]]

    pg_copy(engine, "fact_orders", fact_orders)

    # ============================================================
    # 7. FACT: order_items
    # ============================================================
    print("[fact] order_items")
    with engine.connect() as conn:
        prod_map = dict(conn.execute(text(
            "SELECT product_id, product_key FROM warehouse.dim_products"
        )).fetchall())
        order_rows = conn.execute(text(
            "SELECT order_id, order_key, date_key FROM warehouse.fact_orders"
        )).fetchall()
        order_map = {r[0]: (r[1], r[2]) for r in order_rows}

    fact_items = order_items_df[[
        "order_item_id", "order_id", "product_id",
        "quantity", "unit_price", "line_total",
        "revenue_per_line", "margin_pct"
    ]].copy()

    fact_items["order_key"] = fact_items["order_id"].map(
        {k: v[0] for k, v in order_map.items()}
    ).astype("Int64")
    fact_items["date_key"] = fact_items["order_id"].map(
        {k: v[1] for k, v in order_map.items()}
    ).astype("Int64")
    fact_items["product_key"] = fact_items["product_id"].map(prod_map).astype("Int64")

    fact_items = fact_items[[
        "order_item_id", "order_id", "order_key", "product_key", "date_key",
        "quantity", "unit_price", "line_total", "revenue_per_line", "margin_pct"
    ]]

    pg_copy(engine, "fact_order_items", fact_items)

    # ============================================================
    # Verification
    # ============================================================
    print("\n[verify] warehouse row counts:")
    with engine.connect() as conn:
        for t in ["dim_customers", "dim_products", "dim_date", "dim_payments",
                  "dim_inventory", "fact_orders", "fact_order_items"]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM warehouse.{t}")).scalar()
            print(f"  warehouse.{t:<22} {n:>8,}")

    print("\n✅ Warehouse load complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Warehouse load failed: {e}", file=sys.stderr)
        sys.exit(1)