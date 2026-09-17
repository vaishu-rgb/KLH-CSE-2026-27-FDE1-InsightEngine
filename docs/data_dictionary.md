# InsightEngine — Data Dictionary

Complete reference for every table and column in the platform.

---

## 1. Raw Layer — `insightengine_raw.raw`

All columns are `TEXT` by design (type enforcement happens in validation).

### `raw.customers`

| Column | Type | Description | Example |
|---|---|---|---|
| `customer_id` | TEXT | Unique customer identifier | `CUST000001` |
| `first_name` | TEXT | Customer first name | `Mitchell` |
| `last_name` | TEXT | Customer last name | `Hale` |
| `email` | TEXT | Email (may be null ~2%) | `mitchellkathryn@example.com` |
| `phone` | TEXT | Phone number (free-form) | `779-879-0869` |
| `city` | TEXT | City of residence | `Frankfurt` |
| `country` | TEXT | Country of residence | `Germany` |
| `signup_date` | TEXT | ISO date of signup | `2026-08-07` |
| `segment` | TEXT | Loyalty tier: `bronze`/`silver`/`gold`/`platinum` | `silver` |

### `raw.products`

| Column | Type | Description | Example |
|---|---|---|---|
| `product_id` | TEXT | Unique product identifier | `PROD00001` |
| `product_name` | TEXT | Product name | `Fire Something Toys` |
| `category` | TEXT | Product category (8 total) | `Toys` |
| `brand` | TEXT | Manufacturer brand | `Acme Corp` |
| `price` | TEXT | Selling price (> 0 after validation) | `129.99` |
| `cost` | TEXT | Cost price | `59.99` |
| `created_at` | TEXT | Product creation date | `2024-03-15` |

### `raw.orders`

| Column | Type | Description | Example |
|---|---|---|---|
| `order_id` | TEXT | Unique order identifier (PK) | `ORD00000001` |
| `customer_id` | TEXT | FK to `raw.customers` | `CUST000277` |
| `order_date` | TEXT | Date of order | `2026-03-15` |
| `order_timestamp` | TEXT | Full ISO timestamp | `2026-03-15T17:16:35` |
| `status` | TEXT | `pending`/`shipped`/`delivered`/`cancelled`/`returned` | `delivered` |
| `total_amount` | TEXT | Order total | `1772.64` |
| `currency` | TEXT | ISO currency code | `USD` |

### `raw.order_items`

| Column | Type | Description | Example |
|---|---|---|---|
| `order_item_id` | TEXT | Unique line identifier (PK) | `OI0000000101` |
| `order_id` | TEXT | FK to `raw.orders` | `ORD00000001` |
| `product_id` | TEXT | FK to `raw.products` | `PROD00042` |
| `quantity` | TEXT | Units ordered (> 0 after validation) | `3` |
| `unit_price` | TEXT | Price per unit | `49.99` |
| `line_total` | TEXT | quantity × unit_price | `149.97` |

### `raw.payments`

| Column | Type | Description | Example |
|---|---|---|---|
| `payment_id` | TEXT | Unique payment identifier (PK) | `PAY00000001` |
| `order_id` | TEXT | FK to `raw.orders` | `ORD00000001` |
| `payment_date` | TEXT | Payment date | `2026-03-15` |
| `payment_timestamp` | TEXT | Full ISO timestamp | `2026-03-15T17:45:22` |
| `amount` | TEXT | Amount paid | `1772.64` |
| `method` | TEXT | `credit_card`/`debit_card`/`upi`/`net_banking`/`wallet`/`cod` | `credit_card` |
| `status` | TEXT | `success`/`failed`/`refunded` | `success` |
| `currency` | TEXT | ISO currency code | `USD` |

### `raw.inventory`

| Column | Type | Description | Example |
|---|---|---|---|
| `inventory_id` | TEXT | Unique inventory record (PK) | `INV0000001` |
| `product_id` | TEXT | FK to `raw.products` | `PROD00042` |
| `warehouse` | TEXT | Warehouse code | `WH-North` |
| `quantity_on_hand` | TEXT | Current stock (>= 0 after validation) | `145` |
| `reorder_level` | TEXT | Threshold for reorder (> 0) | `30` |
| `last_updated` | TEXT | Snapshot timestamp | `2026-09-17T06:00:00` |

### `raw.orders_stream`

Streamed orders (from Kafka) with lineage columns.

| Column | Type | Description |
|---|---|---|
| `stream_id` | BIGSERIAL | Auto-increment stream record ID |
| `order_id` | TEXT | Order identifier (unique) |
| `customer_id` | TEXT | FK to customers |
| `order_date` | TEXT | Order date |
| `order_timestamp` | TEXT | Full ISO timestamp |
| `status` | TEXT | Order status |
| `total_amount` | TEXT | Order total |
| `currency` | TEXT | Currency code |
| `kafka_topic` | TEXT | Source Kafka topic |
| `kafka_partition` | INTEGER | Kafka partition |
| `kafka_offset` | BIGINT | Kafka offset |
| `ingested_at` | TIMESTAMPTZ | Ingestion timestamp |

### `raw.ingestion_metadata`

Audit log of every batch load.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Auto-increment |
| `file_name` | TEXT | Source CSV name |
| `target_table` | TEXT | Destination table |
| `row_count` | INTEGER | Rows loaded |
| `loaded_at` | TIMESTAMPTZ | Timestamp |
| `status` | TEXT | `success` or failure reason |

### `raw.validation_metadata`

Audit log of every validation run.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Auto-increment |
| `table_name` | TEXT | Table validated |
| `total_rows` | INTEGER | Rows read |
| `clean_rows` | INTEGER | Rows passing all rules |
| `rejected_rows` | INTEGER | Rows failing any rule |
| `validated_at` | TIMESTAMPTZ | Timestamp |

---

## 2. Warehouse Layer — `insightengine_dw.warehouse`

### `warehouse.dim_customers`

| Column | Type | Description |
|---|---|---|
| `customer_key` | SERIAL | Surrogate key (PK) |
| `customer_id` | TEXT | Natural key (unique) |
| `full_name` | TEXT | Concatenated first + last name |
| `email` | TEXT | Lowercased email |
| `phone` | TEXT | Phone |
| `city` | TEXT | City |
| `country` | TEXT | Country |
| `segment` | TEXT | Loyalty tier |
| `signup_date` | DATE | Signup date |
| `signup_year` | INTEGER | Year of signup |
| `signup_month` | INTEGER | Month of signup |
| `tenure_days` | INTEGER | Days since signup |

### `warehouse.dim_products`

| Column | Type | Description |
|---|---|---|
| `product_key` | SERIAL | Surrogate key (PK) |
| `product_id` | TEXT | Natural key (unique) |
| `product_name` | TEXT | Product name |
| `category` | TEXT | Product category |
| `brand` | TEXT | Brand |
| `price` | NUMERIC(12,2) | Selling price |
| `cost` | NUMERIC(12,2) | Cost price |
| `margin_amount` | NUMERIC(12,2) | price − cost |
| `margin_pct` | NUMERIC(6,2) | Margin as % of price |
| `price_band` | TEXT | `budget`/`mid`/`premium` |
| `created_at` | DATE | Product creation date |

### `warehouse.dim_date`

| Column | Type | Description |
|---|---|---|
| `date_key` | INTEGER | YYYYMMDD (PK) |
| `full_date` | DATE | Calendar date |
| `year` | INTEGER | Year |
| `quarter` | INTEGER | Quarter (1–4) |
| `month` | INTEGER | Month (1–12) |
| `month_name` | TEXT | Month name |
| `day_of_month` | INTEGER | Day (1–31) |
| `day_of_week` | INTEGER | 1 = Sunday, 7 = Saturday |
| `day_name` | TEXT | Day name |
| `is_weekend` | BOOLEAN | Sat or Sun |
| `week_of_year` | INTEGER | Week number |

### `warehouse.dim_payments`

| Column | Type | Description |
|---|---|---|
| `payment_key` | SERIAL | Surrogate key (PK) |
| `payment_id` | TEXT | Natural key (unique) |
| `order_id` | TEXT | Order reference |
| `method` | TEXT | Payment method |
| `status` | TEXT | Payment status |
| `is_success` | BOOLEAN | True if status = `success` |
| `payment_delay_hours` | NUMERIC(10,2) | Hours between order and payment |
| `delay_bucket` | TEXT | `instant`/`same_day`/`within_3_days`/`delayed` |
| `amount` | NUMERIC(12,2) | Payment amount |
| `currency` | TEXT | Currency code |

### `warehouse.dim_inventory`

| Column | Type | Description |
|---|---|---|
| `inventory_key` | SERIAL | Surrogate key (PK) |
| `inventory_id` | TEXT | Natural key (unique) |
| `product_id` | TEXT | Product reference |
| `warehouse` | TEXT | Warehouse code |
| `quantity_on_hand` | INTEGER | Current stock |
| `reorder_level` | INTEGER | Reorder threshold |
| `stock_status` | TEXT | `out_of_stock`/`low`/`healthy` |
| `needs_reorder` | BOOLEAN | True if quantity <= reorder_level |
| `last_updated` | TIMESTAMP | Snapshot timestamp |

### `warehouse.fact_orders`

Grain: one row per order.

| Column | Type | Description |
|---|---|---|
| `order_key` | SERIAL | Surrogate key (PK) |
| `order_id` | TEXT | Natural key (unique) |
| `customer_key` | INTEGER | FK to `dim_customers` |
| `date_key` | INTEGER | FK to `dim_date` |
| `order_timestamp` | TIMESTAMP | Order time |
| `status` | TEXT | Order status |
| `total_amount` | NUMERIC(12,2) | Order total |
| `currency` | TEXT | Currency |
| `order_hour` | INTEGER | Hour of day (0–23) |
| `is_weekend` | BOOLEAN | Weekend flag |

### `warehouse.fact_order_items`

Grain: one row per order line item.

| Column | Type | Description |
|---|---|---|
| `order_item_key` | SERIAL | Surrogate key (PK) |
| `order_item_id` | TEXT | Natural key (unique) |
| `order_id` | TEXT | Order reference |
| `order_key` | INTEGER | FK to `fact_orders` |
| `product_key` | INTEGER | FK to `dim_products` |
| `date_key` | INTEGER | FK to `dim_date` |
| `quantity` | INTEGER | Units ordered |
| `unit_price` | NUMERIC(12,2) | Price per unit |
| `line_total` | NUMERIC(12,2) | quantity × unit_price |
| `revenue_per_line` | NUMERIC(12,2) | Computed revenue |
| `margin_pct` | NUMERIC(6,2) | Product margin % |

---

## 3. Analytics Layer — `insightengine_dw.analytics`

### `analytics.v_daily_revenue`
Daily aggregation of order counts, revenue, and average order value.
**Columns:** `full_date`, `year`, `month`, `month_name`, `day_of_week`, `day_name`, `is_weekend`, `order_count`, `revenue`, `avg_order_value`

### `analytics.v_monthly_revenue`
Monthly aggregation across the full history.
**Columns:** `year`, `month`, `month_name`, `order_count`, `revenue`, `avg_order_value`

### `analytics.v_top_products`
Product-level performance ranked by revenue.
**Columns:** `product_id`, `product_name`, `category`, `brand`, `price_band`, `order_count`, `units_sold`, `revenue`, `avg_margin_pct`

### `analytics.v_category_performance`
Category rollup with revenue and margin.
**Columns:** `category`, `order_count`, `units_sold`, `revenue`, `avg_margin_pct`

### `analytics.v_customer_segments`
Segment × country analysis.
**Columns:** `segment`, `country`, `customer_count`, `order_count`, `revenue`, `avg_order_value`, `revenue_per_customer`

### `analytics.v_payment_success`
Payment method / status / delay bucket breakdown.
**Columns:** `method`, `status`, `delay_bucket`, `payment_count`, `total_amount`, `avg_delay_hours`

### `analytics.v_inventory_health`
Stock status summary by warehouse.
**Columns:** `warehouse`, `stock_status`, `sku_count`, `total_units`, `reorder_alerts`

---

## 4. Attribute Domains

### Customer segment
`bronze` · `silver` · `gold` · `platinum`

### Product category
`Electronics` · `Clothing` · `Home & Kitchen` · `Books` · `Sports` · `Beauty` · `Toys` · `Grocery`

### Order status
`pending` · `shipped` · `delivered` · `cancelled` · `returned`

### Payment method
`credit_card` · `debit_card` · `upi` · `net_banking` · `wallet` · `cod`

### Payment status
`success` · `failed` · `refunded`

### Price band
`budget` (< $50) · `mid` ($50–$300) · `premium` (>= $300)

### Stock status
`out_of_stock` (0 units) · `low` (< reorder level) · `healthy` (>= reorder level)

### Delay bucket
`instant` (< 1 hr) · `same_day` (< 24 hr) · `within_3_days` (< 72 hr) · `delayed` (>= 72 hr)

---

## 5. Referential Integrity

```text
fact_orders.customer_key      → dim_customers.customer_key
fact_orders.date_key          → dim_date.date_key
fact_order_items.order_key    → fact_orders.order_key
fact_order_items.product_key  → dim_products.product_key
fact_order_items.date_key     → dim_date.date_key
```

Foreign keys are enforced by the database. Loader joins on natural keys to resolve surrogate keys.

---

## 6. Lineage

Every record can be traced from source to dashboard:

```text
CSV row
  → raw.<table> (with ingestion_metadata timestamp)
    → <table>_clean.csv
      → Spark Parquet
        → warehouse.dim_* / fact_*
          → analytics view
            → dashboard chart
```

Streaming records also carry `kafka_partition`, `kafka_offset`, and `ingested_at` in `raw.orders_stream`.