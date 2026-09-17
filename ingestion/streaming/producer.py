"""
InsightEngine — Kafka producer for streaming orders.

Reads orders from data/raw/orders.csv and publishes each as a JSON
message to the orders_stream topic, with a small delay between messages
to simulate live arrivals.

Usage:
    python -m ingestion.streaming.producer
    python -m ingestion.streaming.producer --limit 500 --rate 0.01
"""
import argparse
import json
import sys
import time
from datetime import datetime

import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from ingestion.streaming.common import KAFKA_BOOTSTRAP, KAFKA_TOPIC, RAW_DIR


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
        retries=3,
        linger_ms=10,
    )


def stream_orders(limit: int, rate: float, start_offset: int):
    src = RAW_DIR / "orders.csv"
    if not src.exists():
        raise FileNotFoundError(f"missing source: {src}")

    df = pd.read_csv(src)
    df = df.iloc[start_offset:]
    if limit > 0:
        df = df.head(limit)

    print(f"[producer] source  : {src}")
    print(f"[producer] broker  : {KAFKA_BOOTSTRAP}")
    print(f"[producer] topic   : {KAFKA_TOPIC}")
    print(f"[producer] sending : {len(df):,} orders (rate ~{1/rate:.0f}/sec)\n")

    producer = build_producer()
    sent = 0
    t0 = time.time()

    for _, row in df.iterrows():
        event = {
            "order_id": row["order_id"],
            "customer_id": row["customer_id"],
            "order_date": row["order_date"],
            "order_timestamp": row["order_timestamp"],
            "status": row["status"],
            "total_amount": row["total_amount"],
            "currency": row["currency"],
            "emitted_at": datetime.utcnow().isoformat(),
        }
        producer.send(KAFKA_TOPIC, key=row["order_id"], value=event)
        sent += 1

        if sent % 100 == 0:
            producer.flush()
            elapsed = time.time() - t0
            eps = sent / elapsed if elapsed else 0
            print(f"[producer] sent {sent:>6,}  ({eps:>7.1f} events/sec)")

        time.sleep(rate)

    producer.flush()
    producer.close()

    elapsed = time.time() - t0
    print(f"\n[producer] ✅ sent {sent:,} events in {elapsed:.1f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000,
                        help="max events to send (0 = all rows). Default: 1000")
    parser.add_argument("--rate", type=float, default=0.005,
                        help="seconds between events. Default 0.005 (200/sec)")
    parser.add_argument("--start-offset", type=int, default=0,
                        help="skip first N rows of source. Default 0")
    args = parser.parse_args()

    print("=" * 60)
    print("InsightEngine — Kafka Producer (orders_stream)")
    print("=" * 60)

    try:
        stream_orders(args.limit, args.rate, args.start_offset)
    except NoBrokersAvailable:
        print(f"\n❌ Kafka not reachable at {KAFKA_BOOTSTRAP}.\n"
              f"   Is the stack up? Try: docker compose up -d",
              file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Producer failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()