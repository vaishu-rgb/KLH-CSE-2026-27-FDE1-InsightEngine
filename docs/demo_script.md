# InsightEngine — Demo Script

A **5-minute walkthrough** for a faculty demonstration.

---

## Pre-Demo Checklist (run 10 minutes before)

```powershell
# 1. Start the stack
cd C:\Projects\insightengine
docker compose up -d
```

Wait 30 seconds, then confirm 8 services are up:

```powershell
docker compose ps
```

Expected: `ie_postgres_raw`, `ie_postgres_dw`, `ie_postgres_airflow`, `ie_kafka`, `ie_spark`, `ie_spark_worker`, `ie_airflow_webserver`, `ie_airflow_scheduler` — all `Up` (healthy).

```powershell
# 2. Confirm Airflow UI loads
# Open http://localhost:8080  →  admin / admin
```

```powershell
# 3. Pre-warm the Streamlit dashboard
python -m streamlit run dashboard/app.py
# Open http://localhost:8501
```

Have these 4 browser tabs open:
1. **Airflow UI** — http://localhost:8080
2. **Spark UI** — http://localhost:8081
3. **Streamlit Dashboard** — http://localhost:8501
4. **VS Code** — project folder

---

## Demo Script

### 1. Introduction (30 seconds)

> "InsightEngine is an end-to-end data engineering platform that demonstrates the complete data lifecycle — from raw business data to interactive business intelligence. It uses Python, PostgreSQL, Kafka, PySpark, Airflow, and Streamlit, all running in Docker."

Show the `docker-compose.yml` briefly:

> "The entire platform — 8 services including three PostgreSQL instances, Kafka, Spark master and worker, and Airflow — comes up with one command: `docker compose up -d`."

---

### 2. Architecture (45 seconds)

Open `docs/architecture.md` or show the diagram:

> "The pipeline has 10 layers:
> 1. **Data generation** — Python + Faker creates 257,000 rows of realistic business data with intentional imperfections.
> 2. **Dual ingestion** — batch CSVs and Kafka streaming.
> 3. **Raw storage** in PostgreSQL.
> 4. **Validation** that splits clean from rejected with audit logs.
> 5. **PySpark transformations** — 6 jobs producing Parquet.
> 6. **Star schema warehouse** — 5 dimensions + 2 fact tables.
> 7. **Analytics views** powering the dashboard.
> 8. **Python insights layer.**
> 9. **Streamlit BI dashboard.**
> 10. **Full orchestration via Airflow.**"

---

### 3. Trigger the Pipeline (2 minutes — the wow moment)

Switch to **Airflow UI**:

1. Click `insightengine_pipeline`
2. Show the **Graph** view — 8 tasks
3. Click **▶ Trigger DAG**

> "This single click runs the entire pipeline."

Watch the tasks turn green in sequence:

```
01_generate_data      ✅  ~6s
02_load_to_raw        ✅  ~3s
03_validate_raw       ✅  ~5s
04_stream_orders      ✅  ~5s
05_spark_transforms   ✅  ~25s
06_load_warehouse     ✅  ~10s
07_apply_views        ✅  ~2s
08_verify_counts      ✅  ~2s
```

> "End-to-end: about 60 seconds."

While it runs, mention:

> "Every task is idempotent — safe to rerun. Every ingestion and validation is logged to audit tables. Failures retry automatically."

---

### 4. Inspect the Data Layers (1 minute)

Open a terminal:

**Raw layer:**
```powershell
docker exec -it ie_postgres_raw psql -U raw_user -d insightengine_raw -c "SELECT target_table, row_count, status FROM raw.ingestion_metadata;"
```

> "Six tables loaded, all successful, every load audited."

**Validation layer:**
```powershell
docker exec -it ie_postgres_raw psql -U raw_user -d insightengine_raw -c "SELECT table_name, total_rows, clean_rows, rejected_rows FROM raw.validation_metadata;"
```

> "253,101 clean rows, 4,520 rejected — 1.75% rejection rate. Every rejection is traceable."

**Warehouse:**
```powershell
docker exec -it ie_postgres_dw psql -U dw_user -d insightengine_dw -c "\dt warehouse.*"
```

> "5 dimensions, 2 fact tables — a proper star schema."

**Analytics views:**
```powershell
docker exec -it ie_postgres_dw psql -U dw_user -d insightengine_dw -c "\dv analytics.*"
```

> "7 views ready for BI queries."

---

### 5. The Dashboard (1 minute)

Switch to **Streamlit** at http://localhost:8501.

**Overview page:**
> "Live KPIs from the warehouse — $76.5M revenue, 49,667 orders, 5,000 customers."

Drag the **Days slider** from 90 → 365. Chart redraws instantly.

> "Interactive and cached — every chart pulls from the analytics views, not raw tables."

Click **👥 Customers**:
> "Segment analysis by country — bronze in India drives the most volume, gold has the highest revenue-per-customer."

Click **📦 Products**:
> "Top sellers, category margins, and volume-vs-revenue correlation."

Click **⚙️ Operations**:
> "Payment method distribution, delay buckets, and inventory health with reorder alerts."

---

### 6. Close (30 seconds)

> "To summarize: InsightEngine demonstrates the complete data engineering lifecycle —
> **generation → ingestion (batch + streaming) → storage → validation → distributed processing → dimensional modeling → warehousing → analytics → presentation** —
> all orchestrated by a single Airflow DAG, running end-to-end in about 60 seconds.
>
> The code is modular, idempotent, and fully reproducible. Anyone can clone the repo and have the entire platform running in two commands."

---

## Anticipated Questions

**Q: Why three Postgres instances?**
> Separation of concerns — raw can be reloaded without touching warehouse; Airflow metadata isolated from business data.

**Q: Why both batch and streaming?**
> Real pipelines need both — batch for historical data, streaming for live events. The architecture demonstrates both channels feeding the same raw layer.

**Q: Why PySpark for 250k rows?**
> Scale demonstration. The same code runs unchanged on billions of rows with distributed executors. We chose a volume that keeps the demo fast but proves the pattern.

**Q: Why Parquet between Spark and warehouse?**
> Columnar, compressed, schema-embedded, portable — the industry standard for analytical interchange.

**Q: Why two fact tables?**
> Order-level and line-item-level have different grains. Real warehouses separate them to support both kinds of queries efficiently.

**Q: Why raw tables all TEXT?**
> Raw data is allowed to be wrong. Type enforcement happens during validation, with proper error reporting.

**Q: What happens if a task fails?**
> Airflow retries once after 2 minutes. Every stage is idempotent — safe to rerun. Ingestion and validation log every run for auditing.

**Q: Can this scale to production?**
> Yes — swap Docker services for managed equivalents (RDS, MSK, EMR, MWAA) with minimal code changes. The architecture is already production-shaped.

---

## Backup Commands (if something breaks during demo)

**Restart everything:**
```powershell
docker compose restart
```

**Rebuild Airflow images only:**
```powershell
docker compose build airflow-init airflow-webserver airflow-scheduler
docker compose up -d
```

**Rerun the pipeline manually (no Airflow):**
```powershell
python -m generators.run_all
python -m ingestion.batch.load_to_raw
python -m validation.validate_raw
docker exec -it -e PYTHONPATH=/opt/airflow/project ie_airflow_scheduler python /opt/airflow/project/processing/spark_jobs/run_all.py
python -m warehouse.load_warehouse
```

**Rerun just the dashboard:**
```powershell
python -m streamlit run dashboard/app.py
```

**Full clean rebuild (only if absolutely necessary):**
```powershell
docker compose down
docker compose up -d
```
⚠️ **Never** `docker compose down -v` — that deletes volumes and all data.

---

## Timing Summary

| Section | Duration |
|---|---|
| Introduction | 30s |
| Architecture | 45s |
| Trigger Pipeline | 2m |
| Inspect Data Layers | 1m |
| Dashboard | 1m |
| Close | 30s |
| **Total** | **~5 min 45 sec** |

Leaves ~4 minutes for questions and faculty follow-up.