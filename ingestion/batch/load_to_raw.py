"""
InsightEngine — Batch ingestion: CSV -> raw Postgres schema.

Reads each CSV from data/raw and COPYs it into raw.<table>.
Logs each load into raw.ingestion_metadata.

Usage:
    python -m ingestion.batch.load_to_raw
"""
import io
import os
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------- Paths + env ----------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

RAW_DIR = PROJECT_ROOT / "data" / "raw"
SCHEMA_FILE = Path(__file__).resolve().parent / "raw_schema.sql"

# From host machine: localhost. Inside docker: postgres-raw.
RAW_DB_HOST = os.getenv("RAW_DB_HOST", "localhost")
RAW_DB_PORT = os.getenv("POSTGRES_RAW_PORT", "5432")
RAW_DB_USER = os.getenv("POSTGRES_RAW_USER", "raw_user")
RAW_DB_PASS = os.getenv("POSTGRES_RAW_PASSWORD", "raw_pass")
RAW_DB_NAME = os.getenv("POSTGRES_RAW_DB", "insightengine_raw")

RAW_DB_URL = (
    f"postgresql+psycopg2://{RAW_DB_USER}:{RAW_DB_PASS}"
    f"@{RAW_DB_HOST}:{RAW_DB_PORT}/{RAW_DB_NAME}"
)

# ---------- Tables to load ----------
TABLES = [
    ("customers",    "customers.csv"),
    ("products",     "products.csv"),
    ("orders",       "orders.csv"),
    ("order_items",  "order_items.csv"),
    ("payments",     "payments.csv"),
    ("inventory",    "inventory.csv"),
]


def apply_schema(engine):
    """Run raw_schema.sql to (re)create raw tables."""
    print(f"[schema] applying {SCHEMA_FILE.name}")
    ddl = SCHEMA_FILE.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("[schema] raw schema created")


def load_table(engine, table_name: str, csv_file: str):
    """Load a single CSV into raw.<table_name> using COPY for speed."""
    path = RAW_DIR / csv_file
    if not path.exists():
        raise FileNotFoundError(f"missing CSV: {path}")

    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    df = df.where(pd.notna(df), None)  # None instead of NaN for SQL NULL

    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        cur.execute(f"TRUNCATE raw.{table_name};")

        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False, na_rep="\\N")
        buf.seek(0)

        cols = ", ".join(df.columns)
        copy_sql = (
            f"COPY raw.{table_name} ({cols}) "
            f"FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
        )
        cur.copy_expert(copy_sql, buf)
        raw_conn.commit()

        row_count = len(df)
        cur.execute(
            "INSERT INTO raw.ingestion_metadata "
            "(file_name, target_table, row_count, status) "
            "VALUES (%s, %s, %s, %s)",
            (csv_file, f"raw.{table_name}", row_count, "success"),
        )
        raw_conn.commit()
        print(f"[load] raw.{table_name:<14} <- {csv_file:<20} {row_count:>8,} rows")
    except Exception as e:
        raw_conn.rollback()
        try:
            with engine.begin() as c:
                c.execute(
                    text(
                        "INSERT INTO raw.ingestion_metadata "
                        "(file_name, target_table, row_count, status) "
                        "VALUES (:f, :t, 0, :s)"
                    ),
                    {"f": csv_file, "t": f"raw.{table_name}", "s": f"failed: {e}"},
                )
        except Exception:
            pass
        raise
    finally:
        raw_conn.close()


def verify(engine):
    """Print row counts from DB for each raw table."""
    print("\n[verify] row counts in raw schema:")
    with engine.connect() as conn:
        for table, _ in TABLES:
            n = conn.execute(text(f"SELECT COUNT(*) FROM raw.{table}")).scalar()
            print(f"  raw.{table:<14} {n:>10,}")


def main():
    print("=" * 60)
    print("InsightEngine — Batch Ingestion -> raw Postgres")
    print("=" * 60)
    print(f"[conn] {RAW_DB_URL.replace(RAW_DB_PASS, '****')}\n")

    engine = create_engine(RAW_DB_URL, future=True)

    apply_schema(engine)

    for table, csv_file in TABLES:
        load_table(engine, table, csv_file)

    verify(engine)

    print("\n Batch ingestion complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)