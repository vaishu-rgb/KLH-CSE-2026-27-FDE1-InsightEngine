# InsightEngine — System Architecture

Detailed design of the InsightEngine platform: layers, components, data flow, and the reasoning behind the structure.

---

## 1. Design Philosophy

InsightEngine follows four core principles:

| Principle | What it means |
|---|---|
| **Layered architecture** | Each stage has one job. Raw ≠ processed ≠ modeled ≠ presented. |
| **Idempotence** | Every stage can be rerun safely; no duplicates, no corruption. |
| **Observability** | Every ingest and validation is logged to a metadata table. |
| **Reproducibility** | One `docker compose up -d` recreates the entire platform. |

---

## 2. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATION LAYER                       │
│                    Apache Airflow (1 DAG, 8 tasks)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  INGESTION    │    │  PROCESSING   │    │  PRESENTATION │
│               │    │               │    │               │
│  Batch (CSV)  │    │   PySpark     │    │   Streamlit   │
│  Streaming    │    │   6 jobs      │    │   4 pages     │
│  (Kafka)      │    │               │    │               │
└───────┬───────┘    └───────┬───────┘    └───────▲───────┘
        │                    │                    │
        ↓                    ↓                    │
┌───────────────┐    ┌───────────────┐    ┌───────┴───────┐
│  RAW STORAGE  │    │  WAREHOUSE    │    │   ANALYTICS   │
│  PostgreSQL   │    │  PostgreSQL   │───▶│   views +     │
│  raw schema   │    │  star schema  │    │   insights.py │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Data Generation Layer
**Responsibility:** Produce realistic, business-like synthetic data.

| Aspect | Detail |
|---|---|
| Tech | Python, Faker, NumPy, Pandas |
| Location | `generators/` |
| Output | 6 CSVs in `data/raw/` |
| Volume | ~257,000 rows |
| Imperfections | Intentional (~1–2% dirty data injected) |

**Why generated data?** Real business datasets with proper referential integrity, dirty-data patterns, and volumes are hard to source legally. Generation gives us control over every scenario we want to test — including edge cases.

### 3.2 Ingestion Layer
**Responsibility:** Move data into the raw Postgres layer.

Two channels:

**Batch (`ingestion/batch/`)**
- Reads CSVs via Pandas
- Uses PostgreSQL `COPY FROM STDIN` for bulk speed
- Truncates before load → idempotent
- Logs every load to `raw.ingestion_metadata`

**Streaming (`ingestion/streaming/`)**
- Producer publishes JSON events to Kafka topic `orders_stream`
- Consumer subscribes, batches events, upserts into `raw.orders_stream`
- Idempotent on `order_id` via unique index
- Captures partition, offset, timestamp for lineage

### 3.3 Raw Storage Layer
**Responsibility:** Persist data exactly as ingested.

| Aspect | Detail |
|---|---|
| Tech | PostgreSQL 16 |
| Database | `insightengine_raw` |
| Schema | `raw` |
| Tables | 6 raw + 2 audit (`ingestion_metadata`, `validation_metadata`) + `orders_stream` |

**Design choice:** Raw tables use **all TEXT columns**. Type enforcement happens in the validation layer. Why? Because raw data is allowed to be wrong — validation catches that.

### 3.4 Validation Layer
**Responsibility:** Apply business rules, split clean vs rejected.

| Aspect | Detail |
|---|---|
| Tech | Pandas, SQLAlchemy |
| Location | `validation/` |
| Rules | Centralized in `validation/rules.py` |
| Output | `<table>_clean.csv` + `<table>_rejected.csv` |
| Audit | `raw.validation_metadata` |

Rules applied:
- Uniqueness (customer_id, order_id, payment_id)
- Referential integrity (FK checks against parent tables)
- Value domains (segments, statuses, categories)
- Numeric sanity (price > 0, quantity > 0, amount > 0)
- Nullability (critical fields must not be null)

Result: **1.75% rejection rate** — realistic, traceable, auditable.

### 3.5 Processing Layer
**Responsibility:** Distributed transformation, enrichment, derivation.

| Aspect | Detail |
|---|---|
| Tech | Apache Spark 3.5 (PySpark) |
| Location | `processing/spark_jobs/` |
| Jobs | 6 (one per entity) |
| Orchestrator | `run_all.py` |
| Output | Parquet in `data/processed/spark/` |
| Runtime | ~20 seconds for full pipeline |

Transformations include:
- **Joins:** orders→customers, items→products, payments→orders
- **Enrichment:** segments, geography, categories, brands
- **Derivation:** full_name, tenure_days, margin_pct, price_band, delay_bucket, stock_status
- **Date logic:** year, month, day, hour, weekend flag

**Why Parquet?** Columnar, compressed, schema-embedded — the standard format for warehouse ingestion.

### 3.6 Data Warehouse Layer
**Responsibility:** Persist a star schema optimized for analytics.

| Aspect | Detail |
|---|---|
| Tech | PostgreSQL 16 |
| Database | `insightengine_dw` |
| Schema | `warehouse` |
| Dims | `dim_customers`, `dim_products`, `dim_date`, `dim_payments`, `dim_inventory` |
| Facts | `fact_orders` (order grain), `fact_order_items` (line grain) |
| Views | 7 in `analytics` schema |

**Grain decision:** Two fact tables rather than one, to support both order-level and line-level analysis. This mirrors real-world warehouse modeling.

### 3.7 Analytics Layer
**Responsibility:** Clean programmatic access to the warehouse.

| Aspect | Detail |
|---|---|
| Tech | Python, Pandas, SQLAlchemy |
| Location | `analytics/insights.py` |
| Functions | 8 (KPI + 7 view queries) |
| Return type | Pandas DataFrames |

Provides a stable API the dashboard can call without embedding SQL in the UI layer.

### 3.8 Presentation Layer
**Responsibility:** Visualize insights.

| Aspect | Detail |
|---|---|
| Tech | Streamlit + Plotly |
| Location | `dashboard/app.py` |
| Pages | Overview, Customers, Products, Operations |
| Caching | `@st.cache_data(ttl=60)` |

### 3.9 Orchestration Layer
**Responsibility:** Automate the entire pipeline.

| Aspect | Detail |
|---|---|
| Tech | Apache Airflow 2.9 |
| Location | `airflow/dags/insightengine_dag.py` |
| DAG | `insightengine_pipeline` |
| Tasks | 8 sequential |
| Schedule | `@daily` |
| Retries | 1 per task, 2-minute delay |
| Runtime | ~60 seconds end-to-end |

---

## 4. Infrastructure Topology

8 Docker containers on a shared bridge network:

| Container | Image | Purpose | Host Port |
|---|---|---|---|
| `ie_postgres_raw` | postgres:16 | Raw layer | 5432 |
| `ie_postgres_dw` | postgres:16 | Warehouse | 5433 |
| `ie_postgres_airflow` | postgres:16 | Airflow metadata | 5434 |
| `ie_kafka` | confluentinc/cp-kafka:7.6.1 | Streaming broker (KRaft) | 29092 |
| `ie_spark` | apache/spark:3.5.1-python3 | Spark master + UI | 8081 |
| `ie_spark_worker` | apache/spark:3.5.1-python3 | Spark worker | — |
| `ie_airflow_webserver` | insightengine/airflow:latest | Airflow UI | 8080 |
| `ie_airflow_scheduler` | insightengine/airflow:latest | Airflow scheduler | — |

**Why three Postgres instances?** Separation of concerns:
- Raw data can be truncated/reloaded without affecting the warehouse
- Warehouse can be rebuilt independently
- Airflow metadata is isolated (Airflow upgrades won't touch business data)

---

## 5. Data Flow — Full Walkthrough

```text
1. GENERATE
   Python → 6 CSVs (257k rows, ~1.75% dirty)

2. INGEST (batch)
   CSVs → raw.customers, raw.products, raw.orders,
          raw.order_items, raw.payments, raw.inventory

3. INGEST (streaming)
   Producer → Kafka topic → Consumer → raw.orders_stream

4. VALIDATE
   raw.* → clean CSVs + rejected CSVs + validation_metadata

5. PROCESS (PySpark)
   clean CSVs → joins & derivations → 6 Parquet datasets

6. MODEL (warehouse)
   Parquet → dim_* + fact_* tables with surrogate keys

7. VIEWS
   warehouse.* → analytics.v_* (7 aggregate views)

8. ANALYTICS
   analytics.insights.py → pandas DataFrames

9. PRESENT
   Streamlit → interactive BI dashboard
```

---

## 6. Failure Handling

| Stage | Strategy |
|---|---|
| Ingestion | Truncate-then-load (idempotent) |
| Streaming | Upsert on `order_id` (idempotent) |
| Validation | Split clean/reject, never lose rows |
| Spark | Overwrite mode; deterministic output |
| Warehouse | Full rebuild per run |
| Airflow | 1 retry per task, 2-minute delay |

Every stage is safe to rerun.

---

## 7. Environment Configuration

Two contexts run the same code:

| Context | Where it runs | DB host | Port |
|---|---|---|---|
| **Host** (Windows) | Your terminal | `127.0.0.1` | 5432 / 5433 |
| **Docker** | Inside containers | `postgres-raw` / `postgres-dw` | 5432 |

Solved via env vars in `docker-compose.yml` that override `.env` values inside containers. The scripts read `os.getenv(...)` so they work in both places unchanged.

---

## 8. Testing & Observability

- **Ingestion** — every load logged with row count and status
- **Validation** — every run logged with clean/rejected counts
- **Airflow** — every task logged with full stdout/stderr
- **Warehouse** — 7 views act as acceptance tests (row counts sanity-checked by `08_verify_counts`)

---

## 9. Why This Architecture Matters

A working pipeline isn't enough — the **structure** is what makes it maintainable, debuggable, and scalable.

| Layer | Benefit |
|---|---|
| Raw separated from warehouse | Can reload raw without touching analytics |
| Validation split clean/reject | Nothing silently disappears |
| Parquet as interchange format | Columnar, portable, schema-embedded |
| Star schema | Fast BI queries, no joins needed at query time |
| One DAG | Reproducible, monitorable, one-click demo |
| Docker Compose | Runs on any machine with one command |

---

## 10. Extending the Platform

Where to add new functionality:

| Add | Where |
|---|---|
| New data source | `generators/` + `ingestion/` |
| New validation rule | `validation/rules.py` |
| New transformation | `processing/spark_jobs/` |
| New dimension | `warehouse/schema.sql` + `load_warehouse.py` |
| New KPI | `analytics/queries.sql` + `insights.py` |
| New dashboard page | `dashboard/app.py` |
| New pipeline stage | `airflow/dags/insightengine_dag.py` |

Each addition is local — no changes ripple across the whole system.