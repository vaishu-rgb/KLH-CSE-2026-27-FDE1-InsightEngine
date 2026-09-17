"""
Orders transformation:
  - join customers -> segment, country, city
  - derive order_year/month/day/hour, day_of_week
  - is_weekend flag
Output: data/processed/spark/orders/
"""
from pyspark.sql import functions as F

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    orders = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/orders_clean.csv")
    customers = spark.read.parquet(f"{SPARK_OUT_DIR}/customers")

    orders = (
        orders
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("order_timestamp", F.to_timestamp("order_timestamp"))
        .withColumn("order_year", F.year("order_date"))
        .withColumn("order_month", F.month("order_date"))
        .withColumn("order_day", F.dayofmonth("order_date"))
        .withColumn("order_hour", F.hour("order_timestamp"))
        .withColumn("day_of_week", F.dayofweek("order_date"))
        .withColumn(
            "is_weekend",
            F.when(F.dayofweek("order_date").isin(1, 7), True).otherwise(False)
        )
    )

    customer_small = customers.select(
        "customer_id", "segment", "country", "city", "tenure_days"
    )

    joined = orders.join(customer_small, on="customer_id", how="left")

    out = f"{SPARK_OUT_DIR}/orders"
    joined.write.mode("overwrite").parquet(out)
    print(f"[orders] wrote {joined.count():,} rows -> {out}")
    return joined


if __name__ == "__main__":
    spark = get_spark("transform_orders")
    transform(spark)
    spark.stop()