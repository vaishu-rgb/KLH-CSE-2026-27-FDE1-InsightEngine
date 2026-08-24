# InsightEngine: An End-to-End Data Engineering Platform for Business Intelligence

## Project Overview

InsightEngine is an end-to-end, Python-centric data engineering platform
designed to transform raw data from multiple sources into reliable,
structured, and actionable business insights.

The project demonstrates the Data Engineering Lifecycle through data
generation, data ingestion, storage, validation, cleaning, transformation,
data modeling, workflow orchestration, data warehousing, and business
intelligence.

The proposed technology stack includes Python, PostgreSQL, Apache Kafka,
PySpark, Apache Airflow, and Streamlit.

---

## Team Members

| S.No | Name | University ID |
|------|------|---------------|
| 1 | Somu Vaishnavi | 2420030024 |
| 2 | T. Dhanya Sri | 2420030338 |
| 3 | M. Srihitha | 2420030405 |

## Supervisor

**Dr. N Sirisha**

---

## Abstract

InsightEngine is an end-to-end data engineering platform designed to
demonstrate how raw data from multiple sources can be transformed into
reliable and meaningful business insights. The proposed system follows
the complete data engineering lifecycle, including data generation,
batch and streaming ingestion, data storage, data validation, cleaning,
transformation, data modeling, data warehousing, and business
intelligence.

Python serves as the core development language, while PostgreSQL is
used for data storage. Apache Kafka is proposed for streaming data
ingestion, PySpark for scalable data processing, Apache Airflow for
workflow orchestration, and Streamlit for interactive visualization.

The project aims to integrate these components into a modular and
automated pipeline that demonstrates practical data engineering
principles and supports data-driven business analysis.

---

## Technology Stack

- **Python** – Core development and data engineering
- **PostgreSQL** – Data storage
- **Pandas** – Data manipulation
- **Apache Kafka** – Streaming data ingestion
- **PySpark** – Data processing and transformation
- **Apache Airflow** – Workflow orchestration
- **Streamlit** – Business intelligence dashboard
- **Git & GitHub** – Version control and collaboration

---

## Proposed Pipeline

```text
Data Sources
     ↓
Data Generation
     ↓
Data Ingestion
  ┌──┴──┐
Batch  Streaming
  │      │
  │    Kafka
  └──┬───┘
     ↓
PostgreSQL
     ↓
Data Validation & Cleaning
     ↓
PySpark Processing
     ↓
Data Transformation
     ↓
Data Modeling
     ↓
Data Warehouse
     ↓
Streamlit Dashboard
     ↓
Business Insights

Apache Airflow
     ↓
Orchestrates the Pipeline
```
---
## Current Phase Status

**Phase:** Review 1 – Project Proposal and Literature Survey

### Completed
- Project topic finalized
- Problem statement prepared
- Project objectives defined
- Proposed architecture designed
- Technology stack identified
- Literature survey prepared
- Review 1 PPT prepared

### In Progress
- Repository setup
- Initial project structure
- Data source and pipeline planning

### Planned
- Data generation
- Batch data ingestion
- Streaming ingestion using Kafka
- Data validation and cleaning
- PySpark processing
- Data modeling and data warehouse
- Airflow pipeline orchestration
- Streamlit dashboard
---

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/vaishu-rgb/KLH-CSE-2026-27-FDE1-InsightEngine.git
cd KLH-CSE-2026-27-FDE1-InsightEngine
```
---

## Execution Instructions

The proposed execution flow of InsightEngine is:

```text
Data Generation
      ↓
Data Ingestion
      ↓
Data Validation & Cleaning
      ↓
PySpark Processing
      ↓
Data Transformation
      ↓
Data Modeling
      ↓
Data Warehouse
      ↓
Streamlit Dashboard
