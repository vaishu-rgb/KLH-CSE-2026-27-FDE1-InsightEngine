"""
InsightEngine — Master pipeline DAG.

Orchestrates the complete data engineering lifecycle:
  generate -> load_raw -> validate -> stream -> spark -> warehouse -> views -> verify

Schedule: @daily
"""
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# ---------- Paths inside the Airflow container ----------
PROJECT_ROOT = "/opt/airflow/project"

DEFAULT_ARGS = {
    "owner": "insightengine",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


# ============================================================
# Helper: run a Python module as a subprocess
# ============================================================
def run_module(module_name: str, extra_args: list = None):
    """
    Run `python -m <module_name>` from the project root.
    Streams stdout/stderr to the Airflow task log.
    Raises on non-zero exit.
    """
    import subprocess
    import sys

    args = [sys.executable, "-m", module_name] + (extra_args or [])
    print(f"[run_module] cwd={PROJECT_ROOT}")
    print(f"[run_module] cmd={' '.join(args)}")

    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        capture_output=False,   # let it stream to Airflow log
        text=True,
        env={**__import__("os").environ, "PYTHONPATH": PROJECT_ROOT},
    )
    if result.returncode != 0:
        raise RuntimeError(f"module {module_name} failed with exit code {result.returncode}")


# ============================================================
# Task functions
# ============================================================
def task_generate():
    run_module("generators.run_all")


def task_load_raw():
    run_module("ingestion.batch.load_to_raw")


def task_validate():
    run_module("validation.validate_raw")


def task_stream():
    """
    Run producer + consumer in sequence.
    Consumer runs first (short timeout) — if a producer later publishes events,
    it'll be a fresh group run in Phase 7.5+.
    """
    import subprocess
    import sys
    import os

    # 1. Producer — publish a small batch of orders
    print("=" * 60)
    print("Streaming step 1/2: producer")
    print("=" * 60)
    producer = subprocess.run(
        [sys.executable, "-m", "ingestion.streaming.producer",
         "--limit", "500", "--rate", "0.002"],
        cwd=PROJECT_ROOT, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
    )
    if producer.returncode != 0:
        raise RuntimeError(f"producer failed: {producer.returncode}")

    # 2. Consumer — drain whatever's in the topic
    print("=" * 60)
    print("Streaming step 2/2: consumer")
    print("=" * 60)
    consumer = subprocess.run(
        [sys.executable, "-m", "ingestion.streaming.consumer",
         "--max-events", "500", "--idle-timeout", "20"],
        cwd=PROJECT_ROOT, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
    )
    if consumer.returncode != 0:
        raise RuntimeError(f"consumer failed: {consumer.returncode}")


def task_spark():
    """
    Run PySpark transformations inside the same container.
    Uses local[*] master via SPARK_LOCAL_IP=127.0.0.1 env set in docker-compose.
    """
    import subprocess
    import sys
    import os

    spark_script = f"{PROJECT_ROOT}/processing/spark_jobs/run_all.py"
    print(f"[spark] launching {spark_script}")
    result = subprocess.run(
        [sys.executable, spark_script],
        cwd=PROJECT_ROOT, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
    )
    if result.returncode != 0:
        raise RuntimeError(f"spark job failed: {result.returncode}")


def task_load_warehouse():
    run_module("warehouse.load_warehouse")


def task_apply_views():
    """Apply analytics/queries.sql to the warehouse DB."""
    import os
    from sqlalchemy import create_engine, text

    dw_url = os.environ["DW_DB_CONN"]  # set in docker-compose: postgres-dw:5432
    # override with host if needed; inside Airflow container use service name
    print(f"[apply_views] applying analytics/queries.sql")
    ddl_path = Path(PROJECT_ROOT) / "analytics" / "queries.sql"
    ddl = ddl_path.read_text(encoding="utf-8")

    engine = create_engine(dw_url, future=True)
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("[apply_views] ✅ views applied")


def task_verify():
    """Sanity-check row counts across raw + warehouse."""
    import os
    from sqlalchemy import create_engine, text

    raw_url = os.environ["RAW_DB_CONN"]
    dw_url = os.environ["DW_DB_CONN"]

    raw_engine = create_engine(raw_url, future=True)
    dw_engine = create_engine(dw_url, future=True)

    print("=" * 60)
    print("RAW layer")
    print("=" * 60)
    with raw_engine.connect() as conn:
        for t in ["customers", "products", "orders", "order_items", "payments", "inventory"]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM raw.{t}")).scalar()
            print(f"  raw.{t:<18} {n:>8,}")
        n = conn.execute(text("SELECT COUNT(*) FROM raw.orders_stream")).scalar()
        print(f"  raw.orders_stream     {n:>8,}")

    print("\n" + "=" * 60)
    print("WAREHOUSE layer")
    print("=" * 60)
    with dw_engine.connect() as conn:
        for t in ["dim_customers", "dim_products", "dim_date", "dim_payments",
                  "dim_inventory", "fact_orders", "fact_order_items"]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM warehouse.{t}")).scalar()
            print(f"  warehouse.{t:<22} {n:>8,}")
        # quick analytics view test
        rev = conn.execute(text(
            "SELECT ROUND(SUM(revenue)::numeric, 2) FROM analytics.v_monthly_revenue"
        )).scalar()
        print(f"\n  total revenue (all months): ${rev:,}")

    print("\n✅ Verification complete")


# ============================================================
# DAG definition
# ============================================================
with DAG(
    dag_id="insightengine_pipeline",
    description="End-to-end data engineering pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["insightengine", "data-engineering"],
) as dag:

    t1 = PythonOperator(task_id="01_generate_data",    python_callable=task_generate)
    t2 = PythonOperator(task_id="02_load_to_raw",      python_callable=task_load_raw)
    t3 = PythonOperator(task_id="03_validate_raw",     python_callable=task_validate)
    t4 = PythonOperator(task_id="04_stream_orders",    python_callable=task_stream)
    t5 = PythonOperator(task_id="05_spark_transforms", python_callable=task_spark)
    t6 = PythonOperator(task_id="06_load_warehouse",   python_callable=task_load_warehouse)
    t7 = PythonOperator(task_id="07_apply_views",      python_callable=task_apply_views)
    t8 = PythonOperator(task_id="08_verify_counts",    python_callable=task_verify)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8