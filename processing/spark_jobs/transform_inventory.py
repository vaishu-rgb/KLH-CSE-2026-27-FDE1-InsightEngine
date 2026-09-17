"""
Inventory transformation:
  - stock_status (out_of_stock, low, healthy)
  - needs_reorder flag
Output: data/processed/spark/inventory/
"""
from pyspark.sql import functions as F

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/inventory_clean.csv")

    df = (
        df
        .withColumn(
            "stock_status",
            F.when(F.col("quantity_on_hand") == 0, "out_of_stock")
             .when(F.col("quantity_on_hand") < F.col("reorder_level"), "low")
             .otherwise("healthy")
        )
        .withColumn(
            "needs_reorder",
            F.when(F.col("quantity_on_hand") <= F.col("reorder_level"), True)
             .otherwise(False)
        )
        .withColumn("last_updated", F.to_timestamp("last_updated"))
    )

    out = f"{SPARK_OUT_DIR}/inventory"
    df.write.mode("overwrite").parquet(out)
    print(f"[inventory] wrote {df.count():,} rows -> {out}")
    return df


if __name__ == "__main__":
    spark = get_spark("transform_inventory")
    transform(spark)
    spark.stop()