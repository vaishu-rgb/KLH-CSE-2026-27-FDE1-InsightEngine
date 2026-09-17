"""
Order items transformation:
  - join products -> category, brand, price_band
  - revenue_per_line
Output: data/processed/spark/order_items/
"""
from pyspark.sql import functions as F

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    items = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/order_items_clean.csv")
    products = spark.read.parquet(f"{SPARK_OUT_DIR}/products")

    prod_small = products.select(
        "product_id", "category", "brand", "price_band", "margin_pct"
    )

    joined = (
        items
        .join(prod_small, on="product_id", how="left")
        .withColumn("revenue_per_line",
                    F.round(F.col("quantity") * F.col("unit_price"), 2))
    )

    out = f"{SPARK_OUT_DIR}/order_items"
    joined.write.mode("overwrite").parquet(out)
    print(f"[order_items] wrote {joined.count():,} rows -> {out}")
    return joined


if __name__ == "__main__":
    spark = get_spark("transform_order_items")
    transform(spark)
    spark.stop()