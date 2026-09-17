"""
Payments transformation:
  - join orders -> payment delay in hours
  - is_success flag
Output: data/processed/spark/payments/
"""
from pyspark.sql import functions as F

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    payments = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/payments_clean.csv")
    orders = spark.read.parquet(f"{SPARK_OUT_DIR}/orders").select(
        "order_id", "order_timestamp", "customer_id"
    )

    payments = payments.withColumn("payment_timestamp", F.to_timestamp("payment_timestamp"))
    orders_small = orders.withColumnRenamed("order_timestamp", "order_ts")

    joined = (
        payments
        .join(orders_small, on="order_id", how="left")
        .withColumn(
            "payment_delay_hours",
            F.round(
                (F.col("payment_timestamp").cast("long")
                 - F.col("order_ts").cast("long")) / 3600.0,
                2
            )
        )
        .withColumn(
            "is_success",
            F.when(F.col("status") == "success", True).otherwise(False)
        )
        .drop("order_ts")
    )

    out = f"{SPARK_OUT_DIR}/payments"
    joined.write.mode("overwrite").parquet(out)
    print(f"[payments] wrote {joined.count():,} rows -> {out}")
    return joined


if __name__ == "__main__":
    spark = get_spark("transform_payments")
    transform(spark)
    spark.stop()