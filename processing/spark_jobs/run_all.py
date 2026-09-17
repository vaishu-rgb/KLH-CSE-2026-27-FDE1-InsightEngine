"""
Orchestrator — runs all Spark transformations in dependency order.

Usage (inside spark container):
    docker exec -it -e PYTHONPATH=/opt/insightengine ie_spark \\
        /opt/spark/bin/spark-submit \\
        /opt/insightengine/processing/spark_jobs/run_all.py
"""
import time

from processing.spark_jobs.spark_session import get_spark, SPARK_OUT_DIR
from processing.spark_jobs import (
    transform_customers, transform_products, transform_orders,
    transform_order_items, transform_payments, transform_inventory,
)


def main():
    print("=" * 60)
    print("InsightEngine — PySpark Transformations")
    print("=" * 60)

    spark = get_spark("run_all")
    t0 = time.time()

    print("\n[1/6] customers...")
    transform_customers.transform(spark)

    print("\n[2/6] products...")
    transform_products.transform(spark)

    print("\n[3/6] orders (joins customers)...")
    transform_orders.transform(spark)

    print("\n[4/6] order_items (joins products)...")
    transform_order_items.transform(spark)

    print("\n[5/6] payments (joins orders)...")
    transform_payments.transform(spark)

    print("\n[6/6] inventory...")
    transform_inventory.transform(spark)

    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"✅ Spark transformations complete in {elapsed:.1f}s")
    print(f"   Parquet output: {SPARK_OUT_DIR}")
    print("=" * 60)

    spark.stop()


if __name__ == "__main__":
    main()