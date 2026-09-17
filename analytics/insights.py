"""
InsightEngine — Business Analytics layer.

Each function returns a pandas DataFrame answering one business question,
built on the analytics views in the warehouse.

Two ways to use:
    from analytics.insights import daily_revenue
    df = daily_revenue()

    # or via CLI to test all:
    python -m analytics.insights
"""
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ---------- Config ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DW_DB_HOST = os.getenv("DW_DB_HOST", "127.0.0.1")
DW_DB_PORT = os.getenv("POSTGRES_DW_PORT", "5433")
DW_DB_USER = os.getenv("POSTGRES_DW_USER", "dw_user")
DW_DB_PASS = os.getenv("POSTGRES_DW_PASSWORD", "dw_pass")
DW_DB_NAME = os.getenv("POSTGRES_DW_DB", "insightengine_dw")

DW_DB_URL = (
    f"postgresql+psycopg2://{DW_DB_USER}:{DW_DB_PASS}"
    f"@{DW_DB_HOST}:{DW_DB_PORT}/{DW_DB_NAME}"
)

_engine = None


def get_engine():
    """Singleton engine so we don't rebuild connections every query."""
    global _engine
    if _engine is None:
        _engine = create_engine(DW_DB_URL, future=True)
    return _engine


def _query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


# ============================================================
# Business insight functions
# ============================================================

def daily_revenue(days: int = 90) -> pd.DataFrame:
    """Daily revenue + order count for the last N days."""
    sql = """
        SELECT full_date, year, month, month_name, day_name, is_weekend,
               order_count, revenue, avg_order_value
        FROM analytics.v_daily_revenue
        ORDER BY full_date DESC
        LIMIT :days
    """
    return _query(sql, {"days": days})


def monthly_revenue() -> pd.DataFrame:
    """Monthly revenue trend across all time."""
    sql = """
        SELECT year, month, month_name, order_count, revenue, avg_order_value
        FROM analytics.v_monthly_revenue
        ORDER BY year, month
    """
    return _query(sql)


def top_products(limit: int = 20) -> pd.DataFrame:
    """Top products by revenue."""
    sql = """
        SELECT product_id, product_name, category, brand, price_band,
               order_count, units_sold, revenue, avg_margin_pct
        FROM analytics.v_top_products
        ORDER BY revenue DESC
        LIMIT :limit
    """
    return _query(sql, {"limit": limit})


def category_performance() -> pd.DataFrame:
    """Revenue + margin by product category."""
    sql = """
        SELECT category, order_count, units_sold, revenue, avg_margin_pct
        FROM analytics.v_category_performance
        ORDER BY revenue DESC
    """
    return _query(sql)


def customer_segments() -> pd.DataFrame:
    """Revenue by customer segment and country."""
    sql = """
        SELECT segment, country, customer_count, order_count, revenue,
               avg_order_value, revenue_per_customer
        FROM analytics.v_customer_segments
        ORDER BY revenue DESC
    """
    return _query(sql)


def payment_success() -> pd.DataFrame:
    """Payment counts by method + status."""
    sql = """
        SELECT method, status, delay_bucket, payment_count,
               total_amount, avg_delay_hours
        FROM analytics.v_payment_success
        ORDER BY payment_count DESC
    """
    return _query(sql)


def inventory_health() -> pd.DataFrame:
    """Stock status counts by warehouse."""
    sql = """
        SELECT warehouse, stock_status, sku_count, total_units, reorder_alerts
        FROM analytics.v_inventory_health
        ORDER BY warehouse, stock_status
    """
    return _query(sql)


# ============================================================
# KPI summary — headline numbers for the dashboard
# ============================================================

def headline_kpis() -> dict:
    """Return the top-level KPIs as a dict of scalars."""
    sql = """
        SELECT
            (SELECT COUNT(*) FROM warehouse.fact_orders)              AS total_orders,
            (SELECT COUNT(*) FROM warehouse.dim_customers)            AS total_customers,
            (SELECT COUNT(*) FROM warehouse.dim_products)             AS total_products,
            (SELECT ROUND(SUM(revenue)::numeric, 2)
               FROM analytics.v_monthly_revenue)                       AS total_revenue,
            (SELECT ROUND(AVG(avg_order_value)::numeric, 2)
               FROM analytics.v_monthly_revenue)                       AS avg_order_value
    """
    df = _query(sql)
    row = df.iloc[0].to_dict()
    return {k: (int(v) if isinstance(v, (int,)) else float(v) if v is not None else None)
            for k, v in row.items()}


# ============================================================
# CLI: run every insight, print a summary
# ============================================================

def main():
    print("=" * 60)
    print("InsightEngine — Business Insights")
    print("=" * 60)

    print("\n[KPIs]")
    kpis = headline_kpis()
    for k, v in kpis.items():
        print(f"  {k:<20} {v:>14,}" if isinstance(v, (int, float)) else f"  {k:<20} {v}")

    print("\n[daily_revenue] last 5 days:")
    print(daily_revenue(5).to_string(index=False))

    print("\n[monthly_revenue] last 6 months:")
    print(monthly_revenue().tail(6).to_string(index=False))

    print("\n[top_products] top 5:")
    print(top_products(5)[["product_name", "category", "revenue"]].to_string(index=False))

    print("\n[category_performance]:")
    print(category_performance().to_string(index=False))

    print("\n[customer_segments] top 5:")
    print(customer_segments().head(5).to_string(index=False))

    print("\n[payment_success] top 5:")
    print(payment_success().head(5).to_string(index=False))

    print("\n[inventory_health]:")
    print(inventory_health().to_string(index=False))

    print("\n✅ All insights ran successfully")


if __name__ == "__main__":
    main()