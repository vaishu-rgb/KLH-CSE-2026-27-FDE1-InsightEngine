"""Shared Kafka config for producer + consumer."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_HOST_BROKER", "localhost:29092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_ORDERS", "orders_stream")
KAFKA_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "insightengine_orders_consumer")

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"