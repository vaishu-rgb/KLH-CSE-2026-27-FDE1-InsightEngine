"""
InsightEngine — Kafka consumer for orders_stream.

Reads events from the orders_stream topic and writes them into
raw.orders_stream in Postgres. Upserts on order_id so reruns are
idempotent.

Usage:
    python -m ingestion.streaming.consumer
    python -m ingestion.streaming.consumer --max-events 1000 --batch-size 100
"""
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from sqlalchemy import create_engine, text

from ingestion.streaming.common import (
    KAFKA_BOOTSTRAP, KAFKA_TOPIC, KAFKA_GROUP, PROJECT_ROOT
)

# ---------- Raw Postgres connection ----------
import os
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

RAW_DB_HOST = os.getenv("RAW_DB_HOST", "127.0.0.1")
RAW_DB_PORT = os.getenv("POSTGRES_RAW_PORT", "5432")
RAW_DB_USER = os.getenv("POSTGRES_RAW_USER", "raw_user")
RAW_DB_PASS = os.getenv("POSTGRES_RAW_PASSWORD", "raw_pass")
RAW_DB_NAME = os.getenv("POSTGRES_RAW_DB", "insightengine_raw")

RAW_DB_URL = (
    f"postgresql+psycopg2://{RAW_DB_USER}:{RAW_DB_PASS}"
    f"@{RAW_DB_HOST}:{RAW_DB_PORT}/{RAW_DB_NAME}"
)


# ---------- Graceful shutdown ----------
_shutdown = {"flag": False}

def _handle_sigint(signum, frame):
    print("\n[consumer] shutdown requested...")
    _shutdown["flag"] = True

signal.signal(signal.SIGINT, _handle_sigint)


# ---------- DB helpers ----------
def ensure_stream_table(engine):
    ddl_path = Path(__file__).resolve().parent / "stream_schema.sql"
    ddl = ddl_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(ddl))


UPSERT_SQL = text("""
    INSERT INTO raw.orders_stream (
        order_id, customer_id, order_date, order_timestamp,
        status, total_amount, currency,
        kafka_topic, kafka_partition, kafka_offset
    ) VALUES (
        :order_id, :customer_id, :order_date, :order_timestamp,
        :status, :total_amount, :currency,
        :kafka_topic, :kafka_partition, :kafka_offset
    )
    ON CONFLICT (order_id) DO NOTHING;
""")


def flush_batch(engine, batch):
    if not batch:
        return 0
    with engine.begin() as conn:
        for row in batch:
            conn.execute(UPSERT_SQL, row)
    return len(batch)


# ---------- Main consume loop ----------
def consume(max_events: int, batch_size: int, idle_timeout: float):
    engine = create_engine(RAW_DB_URL, future=True)
    ensure_stream_table(engine)
    print(f"[consumer] stream table ready: raw.orders_stream")
    print(f"[consumer] broker: {KAFKA_BOOTSTRAP}")
    print(f"[consumer] topic : {KAFKA_TOPIC}")
    print(f"[consumer] group : {KAFKA_GROUP}\n")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=KAFKA_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=int(idle_timeout * 1000),
    )

    total = 0
    batch = []
    t0 = time.time()

    try:
        for msg in consumer:
            if _shutdown["flag"]:
                break

            e = msg.value
            row = {
                "order_id": e.get("order_id"),
                "customer_id": e.get("customer_id"),
                "order_date": e.get("order_date"),
                "order_timestamp": e.get("order_timestamp"),
                "status": e.get("status"),
                "total_amount": e.get("total_amount"),
                "currency": e.get("currency"),
                "kafka_topic": msg.topic,
                "kafka_partition": msg.partition,
                "kafka_offset": msg.offset,
            }
            batch.append(row)

            if len(batch) >= batch_size:
                n = flush_batch(engine, batch)
                total += n
                batch.clear()
                elapsed = time.time() - t0
                eps = total / elapsed if elapsed else 0
                print(f"[consumer] ingested {total:>6,}  ({eps:>7.1f} events/sec)")

            if max_events and total + len(batch) >= max_events:
                break

    except KeyboardInterrupt:
        pass
    finally:
        if batch:
            n = flush_batch(engine, batch)
            total += n
            batch.clear()
        consumer.close()

    elapsed = time.time() - t0
    print(f"\n[consumer] ✅ ingested {total:,} events in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-events", type=int, default=1000,
                        help="stop after N events (0 = run forever). Default: 1000")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="rows per DB flush. Default: 100")
    parser.add_argument("--idle-timeout", type=float, default=10.0,
                        help="seconds to wait for messages before exiting. Default: 10")
    args = parser.parse_args()

    print("=" * 60)
    print("InsightEngine — Kafka Consumer (orders_stream -> Postgres)")
    print("=" * 60)

    try:
        consume(args.max_events, args.batch_size, args.idle_timeout)
    except NoBrokersAvailable:
        print(f"\n❌ Kafka not reachable at {KAFKA_BOOTSTRAP}.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Consumer failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()