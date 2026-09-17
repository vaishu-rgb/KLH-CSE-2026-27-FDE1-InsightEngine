"""
Shared SparkSession factory + paths for InsightEngine jobs.
"""
import os
from pyspark.sql import SparkSession


def get_spark(app_name: str) -> SparkSession:
    """Return a SparkSession configured for InsightEngine jobs."""
    master = os.getenv("SPARK_MASTER_URL", "local[*]")
    return (
        SparkSession.builder
        .appName(f"InsightEngine::{app_name}")
        .master(master)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.memory", "1g")
        .getOrCreate()
    )


import os

# Path resolution:
#   - spark container:  /opt/insightengine  (default)
#   - airflow container: /opt/airflow/project (set by docker-compose env var)
PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/opt/insightengine")
PROCESSED_DIR = f"{PROJECT_ROOT}/data/processed"
SPARK_OUT_DIR = f"{PROJECT_ROOT}/data/processed/spark"