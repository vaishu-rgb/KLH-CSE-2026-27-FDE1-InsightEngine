-- ============================================================
-- InsightEngine — RAW layer schema
-- Loaded 1:1 from CSVs. All types intentionally loose (TEXT)
-- so dirty data can land. Types are enforced in validation phase.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS raw;

-- ---------- customers ----------
DROP TABLE IF EXISTS raw.customers CASCADE;
CREATE TABLE raw.customers (
    customer_id   TEXT,
    first_name    TEXT,
    last_name     TEXT,
    email         TEXT,
    phone         TEXT,
    city          TEXT,
    country       TEXT,
    signup_date   TEXT,
    segment       TEXT
);

-- ---------- products ----------
DROP TABLE IF EXISTS raw.products CASCADE;
CREATE TABLE raw.products (
    product_id    TEXT,
    product_name  TEXT,
    category      TEXT,
    brand         TEXT,
    price         TEXT,
    cost          TEXT,
    created_at    TEXT
);

-- ---------- orders ----------
DROP TABLE IF EXISTS raw.orders CASCADE;
CREATE TABLE raw.orders (
    order_id         TEXT,
    customer_id      TEXT,
    order_date       TEXT,
    order_timestamp  TEXT,
    status           TEXT,
    total_amount     TEXT,
    currency         TEXT
);

-- ---------- order_items ----------
DROP TABLE IF EXISTS raw.order_items CASCADE;
CREATE TABLE raw.order_items (
    order_item_id  TEXT,
    order_id       TEXT,
    product_id     TEXT,
    quantity       TEXT,
    unit_price     TEXT,
    line_total     TEXT
);

-- ---------- payments ----------
DROP TABLE IF EXISTS raw.payments CASCADE;
CREATE TABLE raw.payments (
    payment_id         TEXT,
    order_id           TEXT,
    payment_date       TEXT,
    payment_timestamp  TEXT,
    amount             TEXT,
    method             TEXT,
    status             TEXT,
    currency           TEXT
);

-- ---------- inventory ----------
DROP TABLE IF EXISTS raw.inventory CASCADE;
CREATE TABLE raw.inventory (
    inventory_id       TEXT,
    product_id         TEXT,
    warehouse          TEXT,
    quantity_on_hand   TEXT,
    reorder_level      TEXT,
    last_updated       TEXT
);

-- ---------- ingestion metadata (audit log) ----------
DROP TABLE IF EXISTS raw.ingestion_metadata CASCADE;
CREATE TABLE raw.ingestion_metadata (
    id             SERIAL PRIMARY KEY,
    file_name      TEXT NOT NULL,
    target_table   TEXT NOT NULL,
    row_count      INTEGER NOT NULL,
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status         TEXT NOT NULL
);