-- ============================================================
-- InsightEngine — Streaming raw table
-- Mirrors raw.orders but adds stream metadata columns.
-- ============================================================

CREATE TABLE IF NOT EXISTS raw.orders_stream (
    stream_id         BIGSERIAL PRIMARY KEY,
    order_id          TEXT,
    customer_id       TEXT,
    order_date        TEXT,
    order_timestamp   TEXT,
    status            TEXT,
    total_amount      TEXT,
    currency          TEXT,
    kafka_topic       TEXT,
    kafka_partition   INTEGER,
    kafka_offset      BIGINT,
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_stream_order_id
    ON raw.orders_stream (order_id);

CREATE INDEX IF NOT EXISTS idx_orders_stream_ingested_at
    ON raw.orders_stream (ingested_at);