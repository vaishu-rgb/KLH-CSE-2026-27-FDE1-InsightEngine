# InsightEngine – An End-to-End Data Engineering Platform for Business Intelligence

> **Raw business data → reliable processed data → analytical warehouse → meaningful business insights**

![Status](https://img.shields.io/badge/status-complete-success)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-compose-2496ED)
![Airflow](https://img.shields.io/badge/orchestration-Airflow_2.9-017CEE)
![Spark](https://img.shields.io/badge/processing-PySpark_3.5-E25A1C)
![Kafka](https://img.shields.io/badge/streaming-Kafka_7.6-231F20)
![PostgreSQL](https://img.shields.io/badge/storage-PostgreSQL_16-336791)

---

## Project Information

| Field | Value |
|---|---|
| **Project Title** | InsightEngine – An End-to-End Data Engineering Platform for Business Intelligence |
| **Course** | Fundamentals of Data Engineering |
| **Academic Year** | 2026–2027 |
| **Section** | 7 |
| **Team Size** | 3 |
| **Guide** | Dr. N. Sirisha |

---

## Team Members

| S. No. | University ID | Name |
|-------:|---------------|------|
| 1 | 2420030024 | Somu Vaishnavi |
| 2 | 2420030338 | T. Dhanya Sri |
| 3 | 2420030405 | M. Srihitha |

---

## 1. Project Overview

Organizations generate large volumes of business data every day — customers, products, orders, payments, inventory — but raw operational data alone does not produce insights. It must be **collected, validated, cleaned, transformed, modeled, stored, and presented** in a structured, reliable form.

**InsightEngine** is a Python-centric, end-to-end data engineering platform that implements the **complete data engineering lifecycle**. It demonstrates how raw business data flows through batch and streaming ingestion, layered storage, distributed processing, dimensional modeling, and warehouse loading — before being converted into interactive business intelligence through a Streamlit dashboard.

The entire pipeline is orchestrated by **Apache Airflow**, allowing the complete workflow to be triggered, monitored, and reproduced from a single interface.

**Current status:** ✅ **Implementation complete** — all 10 pipeline phases are built, tested, and operational end-to-end.

---

## 2. Problem Statement

Traditional business data-processing workflows suffer from:

- Fragmented data sources across multiple systems
- Manual, error-prone preprocessing
- Missing values, duplicate records, and invalid entries
- Inconsistent formats and data types
- Difficulty handling continuously generated (streaming) data
- Poor scalability as data volumes grow
- Limited visibility into data quality and pipeline health
- Difficult, slow business analysis

Raw operational data cannot be trusted or used efficiently without an automated, integrated pipeline.

**InsightEngine addresses these problems** through a fully automated, modular, and reproducible data engineering pipeline that handles batch and streaming data, enforces data quality, builds an analytical warehouse, and presents business insights through an interactive dashboard.

---

## 3. Proposed Solution — Implemented

InsightEngine implements the following end-to-end pipeline:

```text
Business Data Sources
        ↓
Python Data Generation        (5 entities, ~257k rows)
        ↓
Data Ingestion
   ┌────────────┐
   │            │
 Batch       Streaming
  CSV         Kafka
   │            │
   └─────┬──────┘
         ↓
PostgreSQL Raw Storage        (audit-logged loads)
         ↓
Data Validation & Cleaning    (1.75% rows rejected, tracked)
         ↓
PySpark Processing            (6 Spark jobs, Parquet output)
         ↓
Data Modeling — Star Schema   (5 dims + 2 fact tables)
         ↓
PostgreSQL Data Warehouse     (7 analytics views)
         ↓
Business Analytics            (Python insights layer)
         ↓
Streamlit Dashboard           (interactive BI)
         ↓
Business Insights
```

**Apache Airflow** orchestrates the entire pipeline as a single DAG — 8 tasks, end-to-end runtime ≈ **60 seconds**.

---

## 4. Objectives — All Achieved

| # | Objective | Status |
|---|---|---|
| 1 | Collect/generate business data from multiple sources | ✅ |
| 2 | Implement batch and streaming ingestion | ✅ |
| 3 | Build an automated end-to-end pipeline | ✅ |
| 4 | Identify and handle missing, duplicate, invalid data | ✅ |
| 5 | Perform data validation and cleaning | ✅ |
| 6 | Process and transform data using PySpark | ✅ |
| 7 | Implement star-schema data modeling | ✅ |
| 8 | Store processed data in a data warehouse | ✅ |
| 9 | Automate pipeline execution using Airflow | ✅ |
| 10 | Provide an interactive dashboard | ✅ |
| 11 | Generate reliable business insights | ✅ |

---

## 5. Technology Stack

| Technology | Purpose | Version |
|---|---|---|
| **Python** | Core development, generation, orchestration logic | 3.11 |
| **Pandas** | Data manipulation, preprocessing, validation | 2.2 |
| **PostgreSQL** | Raw storage, warehouse, Airflow metadata | 16 |
| **Apache Kafka** | Streaming ingestion (KRaft mode) | 7.6 |
| **Apache Spark (PySpark)** | Distributed transformation & processing | 3.5 |
| **Apache Airflow** | Workflow orchestration & scheduling | 2.9 |
| **Streamlit** | Interactive BI dashboard | 1.40 |
| **Plotly** | Interactive visualizations | 5.24 |
| **SQLAlchemy** | Database access layer | 1.4 |
| **Docker / Docker Compose** | Containerized infrastructure | latest |
| **Git / GitHub** | Version control & collaboration | — |

---

## 6. System Architecture

The system is organized into **layered stages** — each with a single responsibility, clear inputs and outputs, and independent testability.

```text
                    ┌─────────────────────┐
                    │    DATA SOURCES     │
                    │ Customer / Product  │
                    │ Orders / Payments   │
                    │     Inventory       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  DATA GENERATION    │
                    │  Python (Faker)     │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   DATA INGESTION    │
                    │  Batch  │ Streaming │
                    │  CSV    │  Kafka    │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    │   RAW Storage       │
                    │ (6 tables + logs)   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ VALIDATION &        │
                    │ CLEANING            │
                    │ (split clean/reject)│
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │      PySpark        │
                    │  6 Transform Jobs   │
                    │  Parquet Output     │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   DATA MODELING     │
                    │    Star Schema      │
                    │  5 Dims + 2 Facts   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   DATA WAREHOUSE    │
                    │  7 Analytics Views  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  BUSINESS ANALYTICS │
                    │  Python Insights    │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  BUSINESS INSIGHTS  │
                    └─────────────────────┘

                    Apache Airflow
              (Orchestrates the Entire Pipeline)
```

---

## 7. Repository Structure

```text
InsightEngine/
│
├── docker-compose.yml              # 8 services: 3× PostgreSQL, Kafka, Spark master + worker, Airflow
├── .env                            # configuration (never committed)
├── .gitignore
├── README.md
├── requirements.txt                # host-side Python dependencies
│
├── data/                           # data landing zone (gitignored)
│   ├── raw/                        # generated CSVs
│   ├── processed/                  # validated clean + rejected CSVs
│   └── warehouse/                  # (reserved)
│
├── generators/                     # Phase 1 — synthetic data generation
│   ├── config.py
│   ├── generate_customers.py
│   ├── generate_products.py
│   ├── generate_orders.py
│   ├── generate_payments.py
│   ├── generate_inventory.py
│   └── run_all.py
│
├── ingestion/                      # Phases 2 & 4 — batch + streaming
│   ├── batch/
│   │   ├── raw_schema.sql
│   │   └── load_to_raw.py
│   └── streaming/
│       ├── common.py
│       ├── stream_schema.sql
│       ├── producer.py
│       └── consumer.py
│
├── validation/                     # Phase 3 — data quality
│   ├── rules.py
│   └── validate_raw.py
│
├── processing/                     # Phase 5 — PySpark transformations
│   └── spark_jobs/
│       ├── spark_session.py
│       ├── transform_customers.py
│       ├── transform_products.py
│       ├── transform_orders.py
│       ├── transform_order_items.py
│       ├── transform_payments.py
│       ├── transform_inventory.py
│       └── run_all.py
│
├── warehouse/                      # Phase 6 — star schema
│   ├── schema.sql
│   └── load_warehouse.py
│
├── airflow/                        # Phase 7 — orchestration
│   ├── Dockerfile                  # custom image: PySpark + Java + project deps
│   ├── requirements.txt
│   └── dags/
│       └── insightengine_dag.py
│
├── analytics/                      # Phase 8 — business insights
│   ├── insights.py
│   └── queries.sql
│
├── dashboard/                      # Phase 9 — Streamlit BI
│   └── app.py
│
└── docs/                           # Phase 10 — documentation
    ├── architecture.md
    ├── data_dictionary.md
    └── demo_script.md
```

---

## 8. Data Pipeline — Stage by Stage

### Stage 1 — Data Generation
Python + Faker generate realistic business data across **5 entities**:

| Entity | Rows Generated | Rows After Validation |
|---|---:|---:|
| Customers | 5,000 | 5,000 |
| Products | 500 | 496 |
| Orders | 50,250 | 49,667 |
| Order Items | 152,357 | 149,208 |
| Payments | 47,811 | 47,027 |
| Inventory | 1,703 | 1,703 |
| **Total** | **257,621** | **253,101** |

Realistic imperfections are intentionally injected (nulls, negative prices, duplicates, invalid statuses) to give the validation layer genuine work.

### Stage 2 — Batch Ingestion
Pandas + PostgreSQL `COPY` load each CSV into `raw.*` tables. Every load is recorded in `raw.ingestion_metadata` for auditability.

### Stage 3 — Data Validation & Cleaning
Rule-based validation splits each table into **clean** and **rejected** records:

| Table | Clean | Rejected | Rejection % |
|---|---:|---:|---:|
| customers | 5,000 | 0 | 0% |
| products | 496 | 4 | 0.80% |
| orders | 49,667 | 583 | 1.16% |
| order_items | 149,208 | 3,149 | 2.07% |
| payments | 47,027 | 784 | 1.64% |
| inventory | 1,703 | 0 | 0% |
| **Total** | **253,101** | **4,520** | **1.75%** |

Results are logged to `raw.validation_metadata`.

### Stage 4 — Streaming Ingestion (Kafka)
A producer publishes order events to the `orders_stream` Kafka topic. A consumer subscribes and writes them into `raw.orders_stream` with idempotent upserts on `order_id`. Stream metadata (`kafka_partition`, `kafka_offset`, `ingested_at`) is captured for lineage.

### Stage 5 — PySpark Transformations
Six Spark jobs read the clean CSVs, apply joins, aggregations, and derived-column logic, and write **Parquet** output for warehouse ingestion:

- **Customers** — full name, signup year/month, tenure in days
- **Products** — margin amount & %, price band (budget / mid / premium)
- **Orders** — enriched with customer segment, country, city; derived date parts, weekend flag
- **Order Items** — joined to products; revenue per line
- **Payments** — payment delay in hours, success flag, delay bucket
- **Inventory** — stock status (out_of_stock / low / healthy), reorder flag

### Stage 6 — Star Schema Modeling
The warehouse Postgres instance (`insightengine_dw`) holds:

**Dimension tables**
- `dim_customers`
- `dim_products`
- `dim_date` (generated calendar, YYYYMMDD key)
- `dim_payments`
- `dim_inventory`

**Fact tables**
- `fact_orders` — one row per order (order-level grain)
- `fact_order_items` — one row per order line (line-level grain)

Surrogate keys are assigned during load; foreign keys link facts to dimensions.

### Stage 7 — Analytics Views
Seven SQL views sit on top of the warehouse and power the dashboard:

- `v_daily_revenue`
- `v_monthly_revenue`
- `v_top_products`
- `v_category_performance`
- `v_customer_segments`
- `v_payment_success`
- `v_inventory_health`

### Stage 8 — Business Analytics Layer
`analytics/insights.py` exposes typed Python functions (e.g., `daily_revenue()`, `top_products()`, `headline_kpis()`) that query the views and return pandas DataFrames — providing a clean data-access layer for the dashboard.

### Stage 9 — Streamlit Dashboard
A four-page interactive BI dashboard:

| Page | What it shows |
|---|---|
| **Overview** | Headline KPIs, daily & monthly revenue trends, category performance |
| **Customers** | Segment analysis, geographic distribution, revenue per customer |
| **Products** | Top sellers, category margins, volume vs revenue |
| **Operations** | Payment methods, delay distribution, inventory health |

All charts are interactive (Plotly). Data is cached for 60 seconds for responsiveness.

### Stage 10 — Airflow Orchestration
A single DAG (`insightengine_pipeline`) chains all 8 stages sequentially:

```
01_generate_data  →  02_load_to_raw  →  03_validate_raw  →  04_stream_orders
   →  05_spark_transforms  →  06_load_warehouse  →  07_apply_views  →  08_verify_counts
```

- **Schedule:** `@daily`
- **Retries:** 1 per task, 2-minute delay
- **Runtime:** ≈ 60 seconds end-to-end
- **Monitoring:** Full Airflow UI at `http://localhost:8080`

---

## 9. Data Model

```text
                        ┌───────────────────┐
                        │  dim_customers    │
                        └─────────┬─────────┘
                                  │
                                  │
┌───────────────────┐   ┌─────────▼──────────┐   ┌───────────────────┐
│  dim_products     │──▶│   fact_orders      │◀──│   dim_date        │
└─────────┬─────────┘   └─────────┬──────────┘   └───────────────────┘
          │                       │
          │                       │
          │             ┌─────────▼──────────┐
          │             │ fact_order_items   │
          │             └─────────┬──────────┘
          │                       │
┌─────────▼─────────┐   ┌─────────▼──────────┐
│  dim_inventory    │   │   dim_payments     │
└───────────────────┘   └────────────────────┘
```

Facts store **measurable events**; dimensions store **descriptive context**.

---

## 10. Setup Instructions

### Prerequisites

- **Docker Desktop** (with WSL 2 backend on Windows)
- **Python 3.11+**
- **~6 GB free RAM** for all containers
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/vaishu-rgb/KLH-CSE-2026-27-FDE1-InsightEngine.git
cd KLH-CSE-2026-27-FDE1-InsightEngine
```

### 2. Configure Environment

Copy the sample environment and fill in values:

```bash
cp .env.example .env
```

The `.env` holds database credentials, ports, and Kafka config. **Never commit `.env`** — it is already in `.gitignore`.

### 3. Start All Services

```bash
docker compose up -d
```

This brings up **8 containers**:

| Service | Purpose | Host Port |
|---|---|---|
| `postgres-raw` | Raw data layer | 5432 |
| `postgres-dw` | Data warehouse | 5433 |
| `postgres-airflow` | Airflow metadata | 5434 |
| `kafka` | Streaming broker | 29092 |
| `spark` | Spark master (UI) | 8081 |
| `spark-worker` | Spark worker | — |
| `airflow-webserver` | Airflow UI | 8080 |
| `airflow-scheduler` | Airflow scheduler | — |

### 4. Install Local Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Access the Interfaces

| Interface | URL | Credentials |
|---|---|---|
| Airflow UI | http://localhost:8080 | `admin` / `admin` |
| Spark Master UI | http://localhost:8081 | — |
| Streamlit Dashboard | http://localhost:8501 | — |

---

## 11. Execution Instructions

### Option A — Automated (recommended)

Trigger the full pipeline from Airflow:

1. Open http://localhost:8080 → login `admin` / `admin`
2. Unpause the `insightengine_pipeline` DAG
3. Click **▶ Trigger DAG**
4. Watch all 8 tasks complete in ~60 seconds

Or via CLI:

```bash
docker exec -it ie_airflow_scheduler airflow dags trigger insightengine_pipeline
```

### Option B — Manual, step by step

```bash
python -m generators.run_all             # 1. Generate synthetic data
python -m ingestion.batch.load_to_raw    # 2. Load raw CSVs → Postgres
python -m validation.validate_raw        # 3. Validate & clean
python -m ingestion.streaming.producer   # 4. Stream orders to Kafka
python -m ingestion.streaming.consumer   #    Consume → raw.orders_stream
# 5. PySpark transformations
docker exec -it -e PYTHONPATH=/opt/insightengine ie_spark \
    /opt/spark/bin/spark-submit \
    /opt/insightengine/processing/spark_jobs/run_all.py
python -m warehouse.load_warehouse       # 6. Build star-schema warehouse
```

### Option C — Launch the Dashboard

```bash
python -m streamlit run dashboard/app.py
```

Opens at http://localhost:8501.

---

## 12. Key Results

After a full pipeline run:

| Metric | Value |
|---|---:|
| Rows generated | 257,621 |
| Rows passed validation | 253,101 (98.25%) |
| Rows rejected (tracked) | 4,520 (1.75%) |
| Streaming events ingested | 1,000 |
| Warehouse dimension rows | 54,229 |
| Warehouse fact rows | 198,875 |
| Analytics views | 7 |
| Airflow tasks per run | 8 |
| End-to-end runtime | ≈ 60 seconds |

**Business KPIs produced by the dashboard:**
- Total revenue, total orders, unique customers, product count, average order value
- Daily and monthly revenue trends
- Category-level performance with margins
- Customer segment & country analysis
- Payment method distribution and delay buckets
- Inventory health with reorder alerts

---

## 13. Implementation Status

| Phase | Component | Status |
|---|---|---|
| 0 | Docker infrastructure (8 services) | ✅ Complete |
| 1 | Synthetic data generation | ✅ Complete |
| 2 | Batch ingestion → raw Postgres | ✅ Complete |
| 3 | Data validation & preprocessing | ✅ Complete |
| 4 | Kafka streaming ingestion | ✅ Complete |
| 5 | PySpark transformations | ✅ Complete |
| 6 | Star-schema data warehouse | ✅ Complete |
| 7 | Airflow orchestration | ✅ Complete |
| 8 | Business analytics layer | ✅ Complete |
| 9 | Streamlit dashboard | ✅ Complete |
| 10 | Documentation | ✅ Complete |

**The pipeline runs end-to-end and is fully reproducible.**

---

## 14. Data Security

The repository **does not** and **will not** contain:

- Passwords or API keys
- Database credentials
- Authentication tokens
- Confidential institutional data
- Licensed datasets without permission

Sensitive configuration is managed through `.env` files, which are excluded from version control via `.gitignore`.

---

## 15. Future Scope

Potential improvements building on the current platform:

- Real-time streaming analytics (integrate Kafka → Spark Streaming → warehouse)
- Cloud deployment (AWS / GCP managed Postgres, MSK, EMR, MWAA)
- Machine learning integration (churn prediction, demand forecasting)
- Advanced data-quality monitoring and automated alerts
- Anomaly detection on order patterns and payment failures
- Additional data sources (web analytics, CRM, support tickets)
- Data catalogs and lineage tracking
- CI/CD for DAG deployments and pipeline tests
- Predictive dashboards embedded in the Streamlit UI

---

## 16. Conclusion

**InsightEngine** demonstrates the complete data engineering lifecycle in a single, reproducible, Python-centric platform. It combines Python, PostgreSQL, Apache Kafka, PySpark, Apache Airflow, and Streamlit to build an automated and modular pipeline that transforms raw business data into reliable, structured, and meaningful information.

Every stage is **idempotent, observable, and independently testable**, and the entire workflow is **orchestrated from a single Airflow DAG**. The project shows not only that a pipeline can work, but *how* each layer — ingestion, storage, validation, processing, modeling, warehousing, analytics, and presentation — contributes to turning raw operational data into trustworthy business insight.

---

## 17. Acknowledgement

This project is developed as part of the **Fundamentals of Data Engineering** course for the academic year **2026–2027**.

The team acknowledges the guidance and support provided by **Dr. N. Sirisha** throughout the project development process.

---

## Project Repository

**GitHub:** [https://github.com/vaishu-rgb/KLH-CSE-2026-27-FDE1-InsightEngine](https://github.com/vaishu-rgb/KLH-CSE-2026-27-FDE1-InsightEngine)

---

## License

MIT — free to learn from, fork, and extend.
