"""
Products transformation:
  - margin_amount, margin_pct
  - price_band (budget/mid/premium)
Output: data/processed/spark/products/
"""
from pyspark.sql import functions as F

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/products_clean.csv")

    df = (
        df
        .withColumn("margin_amount", F.round(F.col("price") - F.col("cost"), 2))
        .withColumn(
            "margin_pct",
            F.when(F.col("price") > 0,
                   F.round((F.col("price") - F.col("cost")) / F.col("price") * 100, 2))
             .otherwise(F.lit(0.0))
        )
        .withColumn(
            "price_band",
            F.when(F.col("price") < 50, "budget")
             .when(F.col("price") < 300, "mid")
             .otherwise("premium")
        )
        .withColumn("created_at", F.to_date("created_at"))
    )

    out = f"{SPARK_OUT_DIR}/products"
    df.write.mode("overwrite").parquet(out)
    print(f"[products] wrote {df.count():,} rows -> {out}")
    return df


if __name__ == "__main__":
    spark = get_spark("transform_products")
    transform(spark)
    spark.stop()