"""
Customers transformation:
  - lowercase/trim email
  - full_name derived
  - signup_year, signup_month, tenure_days
Output: data/processed/spark/customers/
"""
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

from processing.spark_jobs.spark_session import get_spark, PROCESSED_DIR, SPARK_OUT_DIR


def transform(spark):
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{PROCESSED_DIR}/customers_clean.csv")

    df = (
        df
        .withColumn("email", F.lower(F.trim(F.col("email"))))
        .withColumn("full_name", F.concat_ws(" ", F.col("first_name"), F.col("last_name")))
        .withColumn("signup_date", F.to_date("signup_date"))
        .withColumn("signup_year", F.year("signup_date"))
        .withColumn("signup_month", F.month("signup_date"))
        .withColumn(
            "tenure_days",
            F.datediff(F.current_date(), F.col("signup_date")).cast(IntegerType())
        )
        .withColumn("segment", F.lower(F.col("segment")))
        .drop("first_name", "last_name")
    )

    out = f"{SPARK_OUT_DIR}/customers"
    df.write.mode("overwrite").parquet(out)
    print(f"[customers] wrote {df.count():,} rows -> {out}")
    return df


if __name__ == "__main__":
    spark = get_spark("transform_customers")
    transform(spark)
    spark.stop()