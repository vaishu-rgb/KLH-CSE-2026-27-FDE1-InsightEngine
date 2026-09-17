-- ============================================================
-- InsightEngine — Star Schema Warehouse DDL
-- Runs in insightengine_dw Postgres
-- ============================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

-- ============================================================
-- DIMENSION: customers
-- ============================================================
DROP TABLE IF EXISTS warehouse.dim_customers CASCADE;
CREATE TABLE warehouse.dim_customers (
    customer_key    SERIAL PRIMARY KEY,
    customer_id     TEXT NOT NULL UNIQUE,
    full_name       TEXT,
    email           TEXT,
    phone           TEXT,
    city            TEXT,
    country         TEXT,
    segment         TEXT,
    signup_date     DATE,
    signup_year     INTEGER,
    signup_month    INTEGER,
    tenure_days     INTEGER
);
CREATE INDEX idx_dim_customers_segment ON warehouse.dim_customers (segment);
CREATE INDEX idx_dim_customers_country ON warehouse.dim_customers (country);

-- ============================================================
-- DIMENSION: products
-- ============================================================
DROP TABLE IF EXISTS warehouse.dim_products CASCADE;
CREATE TABLE warehouse.dim_products (
    product_key     SERIAL PRIMARY KEY,
    product_id      TEXT NOT NULL UNIQUE,
    product_name    TEXT,
    category        TEXT,
    brand           TEXT,
    price           NUMERIC(12,2),
    cost            NUMERIC(12,2),
    margin_amount   NUMERIC(12,2),
    margin_pct      NUMERIC(6,2),
    price_band      TEXT,
    created_at      DATE
);
CREATE INDEX idx_dim_products_category ON warehouse.dim_products (category);
CREATE INDEX idx_dim_products_band ON warehouse.dim_products (price_band);

-- ============================================================
-- DIMENSION: date
-- ============================================================
DROP TABLE IF EXISTS warehouse.dim_date CASCADE;
CREATE TABLE warehouse.dim_date (
    date_key        INTEGER PRIMARY KEY,   -- YYYYMMDD
    full_date       DATE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    month_name      TEXT NOT NULL,
    day_of_month    INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,      -- 1=Sun..7=Sat
    day_name        TEXT NOT NULL,
    is_weekend      BOOLEAN NOT NULL,
    week_of_year    INTEGER NOT NULL
);

-- ============================================================
-- DIMENSION: payments
-- ============================================================
DROP TABLE IF EXISTS warehouse.dim_payments CASCADE;
CREATE TABLE warehouse.dim_payments (
    payment_key         SERIAL PRIMARY KEY,
    payment_id          TEXT NOT NULL UNIQUE,
    order_id            TEXT,
    method              TEXT,
    status              TEXT,
    is_success          BOOLEAN,
    payment_delay_hours NUMERIC(10,2),
    delay_bucket        TEXT,
    amount              NUMERIC(12,2),
    currency            TEXT
);
CREATE INDEX idx_dim_payments_status ON warehouse.dim_payments (status);
CREATE INDEX idx_dim_payments_method ON warehouse.dim_payments (method);

-- ============================================================
-- DIMENSION: inventory
-- ============================================================
DROP TABLE IF EXISTS warehouse.dim_inventory CASCADE;
CREATE TABLE warehouse.dim_inventory (
    inventory_key      SERIAL PRIMARY KEY,
    inventory_id       TEXT NOT NULL UNIQUE,
    product_id         TEXT,
    warehouse          TEXT,
    quantity_on_hand   INTEGER,
    reorder_level      INTEGER,
    stock_status       TEXT,
    needs_reorder      BOOLEAN,
    last_updated       TIMESTAMP
);
CREATE INDEX idx_dim_inventory_status ON warehouse.dim_inventory (stock_status);

-- ============================================================
-- FACT: orders (order-level grain)
-- ============================================================
DROP TABLE IF EXISTS warehouse.fact_orders CASCADE;
CREATE TABLE warehouse.fact_orders (
    order_key        SERIAL PRIMARY KEY,
    order_id         TEXT NOT NULL UNIQUE,
    customer_key     INTEGER REFERENCES warehouse.dim_customers(customer_key),
    date_key         INTEGER REFERENCES warehouse.dim_date(date_key),
    order_timestamp  TIMESTAMP,
    status           TEXT,
    total_amount     NUMERIC(12,2),
    currency         TEXT,
    order_hour       INTEGER,
    is_weekend       BOOLEAN
);
CREATE INDEX idx_fact_orders_customer ON warehouse.fact_orders (customer_key);
CREATE INDEX idx_fact_orders_date ON warehouse.fact_orders (date_key);
CREATE INDEX idx_fact_orders_status ON warehouse.fact_orders (status);

-- ============================================================
-- FACT: order_items (line-level grain)
-- ============================================================
DROP TABLE IF EXISTS warehouse.fact_order_items CASCADE;
CREATE TABLE warehouse.fact_order_items (
    order_item_key   SERIAL PRIMARY KEY,
    order_item_id    TEXT NOT NULL UNIQUE,
    order_id         TEXT,
    order_key        INTEGER REFERENCES warehouse.fact_orders(order_key),
    product_key      INTEGER REFERENCES warehouse.dim_products(product_key),
    date_key         INTEGER REFERENCES warehouse.dim_date(date_key),
    quantity         INTEGER,
    unit_price       NUMERIC(12,2),
    line_total       NUMERIC(12,2),
    revenue_per_line NUMERIC(12,2),
    margin_pct       NUMERIC(6,2)
);
CREATE INDEX idx_fact_items_order ON warehouse.fact_order_items (order_key);
CREATE INDEX idx_fact_items_product ON warehouse.fact_order_items (product_key);
CREATE INDEX idx_fact_items_date ON warehouse.fact_order_items (date_key);