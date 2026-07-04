# Irish Grid Carbon Intensity Tracker

A production-style data engineering pipeline tracking Ireland's electricity 
generation mix and carbon intensity across 6 energy sources (wind, gas, coal, 
hydro, solar, interconnector).

Built as a **Local-to-Cloud Evolution** project: Phase 1 runs entirely on 
Docker for $0. Phase 2 migrates to GCP Always-Free tier.

---

## Architecture

```
PHASE 1 - LOCAL ($0)                    PHASE 2 - CLOUD (GCP Free Tier)

Synthetic EirGrid Data Generator        EirGrid API / Met Eireann API
|                                       |
v                                       v
Python Ingestion Script                 Python Ingestion (Cloud Function)
|                                       |
v                                       v
/data/raw (NDJSON, local disk)          GCS Bucket (raw zone, 5GB free)
|                                       |
v                                       v
PySpark Transform local[*]              PySpark / BigQuery SQL Transform
Bronze -> Silver (Parquet)              Bronze -> Silver -> Gold (BigQuery)
|                                       |
v                                       v
PostgreSQL Star Schema                  BigQuery Star Schema (1TB/mo free)
|                                       |
v                                       v
Apache Airflow DAG                      Airflow on GCP e2-micro VM
(Dockerized, local scheduler)           (Always Free, ~$0/mo)

```

## Tech Stack

| Layer | Local (Phase 1) | Cloud (Phase 2) |
|---|---|---|
| Ingestion | Python | Python + Cloud Functions |
| Storage | Local filesystem | GCS Bucket |
| Transform | PySpark 3.5 (local mode) | PySpark / BigQuery SQL |
| Warehouse | PostgreSQL 15 | BigQuery |
| Orchestration | Apache Airflow 2.9 | Airflow on e2-micro VM |
| Containerisation | Docker + Compose | Cloud Run / GCE |

```

## Schema Design (Star Schema)

dim_time -----+
+--> fact_generation
dim_source ---+
- `fact_generation`: generation_mw, carbon_intensity per source per day
- `dim_time`: date, year, month, day
- `dim_source`: wind, gas, coal, hydro, solar, interconnector

```

## Key Engineering Decisions

- **Rejected Cloud Composer** (~$300/mo minimum) in favour of self-managed 
  Airflow on GCP Always-Free e2-micro VM
- **Medallion architecture**: raw NDJSON -> Parquet (Silver) -> 
  PostgreSQL/BigQuery (Gold)
- **Idempotent loads**: INSERT ON CONFLICT DO UPDATE prevents duplicate rows 
  on DAG reruns
- **Explicit PySpark schema**: never infer schema on production pipelines, 
  catches upstream API changes immediately
- **Local-mode Spark**: local[*] in Phase 1 keeps infrastructure simple; 
  same transform code runs on cluster in Phase 2 with zero changes

```

## Running Locally

### Prerequisites
- Docker Desktop
- Git

### Start the pipeline

```bash
docker-compose -f docker-compose.yml up -d
```

### Access services

| Service | URL | Credentials |
|---|---|---|
| Airflow UI | http://localhost:8080 | admin / admin |
| Spark Master UI | http://localhost:8081 | - |
| PostgreSQL | localhost:5432 | airflow / airflow |

### Trigger a pipeline run

1. Open http://localhost:8080
2. Enable the `ingest_grid_data` DAG
3. Click Trigger DAG
4. Watch: fetch_grid_data -> bronze_to_silver -> silver_to_gold

### Verify data in Postgres

```sql
SELECT dt.date, ds.source_name, fg.generation_mw, fg.carbon_intensity
FROM fact_generation fg
JOIN dim_time dt ON fg.time_id = dt.time_id
JOIN dim_source ds ON fg.source_id = ds.source_id
ORDER BY dt.date, ds.source_name;
```

```

## Repository Structure

ireland-grid-carbon-tracker/
|-- dags/
|   |-- dags_ingest.py          # Airflow DAG: fetch -> transform -> load
|-- src/
|   |-- ingestion/
|   |   |-- fetch_eirgrid.py    # Data ingestion (synthetic generator)
|   |-- transform/
|       |-- bronze_to_silver.py # PySpark: NDJSON -> Parquet
|       |-- silver_to_gold.py   # Pandas: Parquet -> PostgreSQL upsert
|-- sql/
|   |-- ddl/
|       |-- schema.sql          # Star schema DDL
|-- docker/
|   |-- airflow/
|       |-- Dockerfile          # Custom Airflow image with Java + PySpark
|-- docker-compose.yml          # Full local stack definition

```

## Profile Summary (for LinkedIn/CV)

- Built a renewable-energy analytics pipeline on a fully Dockerized local 
  stack, migrating to GCP Always-Free architecture at $0 ongoing cost
- Implemented Medallion architecture (Bronze/Silver/Gold) with PySpark 3.5 
  and Apache Airflow 2.9 orchestration
- Enforced idempotent loads via PostgreSQL upsert patterns, preventing data 
  duplication on pipeline reruns
- Rejected Cloud Composer (~$300/mo) in favour of cost-aware architecture 
  using GCP Always-Free e2-micro VM

```

## Phase 2: GCP Migration (In Progress)

- [x] GCS bucket for raw zone
- [x] BigQuery star schema
- [x] Airflow on e2-micro Always-Free VM
- [x] Cloud Function for ingestion trigger
- [ ] Cost guardrail CI check (BigQuery dry-run)
- [ ] GitHub Actions CI/CD pipeline
