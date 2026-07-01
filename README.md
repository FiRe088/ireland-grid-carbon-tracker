# Irish Grid Carbon Intensity Tracker

A production-style data engineering pipeline tracking Ireland's electricity generation mix and carbon intensity across 6 energy sources (wind, gas, coal, hydro, solar, interconnector).

Built as a **Local-to-Cloud Evolution** project: Phase 1 runs entirely on Docker for $0. Phase 2 migrates to GCP Always-Free tier.

## Architecture
PHASE 1 â€” LOCAL ($0)                    PHASE 2 â€” CLOUD (GCP Free Tier)
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€   â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Synthetic EirGrid Data Generator        EirGrid API / Met Ã‰ireann API
â”‚                                        â”‚
â–¼                                        â–¼
Python Ingestion Script               Python Ingestion (Cloud Function)
â”‚                                        â”‚
â–¼                                        â–¼
/data/raw (NDJSON, local disk)        GCS Bucket (raw zone, 5GB free)
â”‚                                        â”‚
â–¼                                        â–¼
PySpark Transform (local[*])          PySpark / BigQuery SQL Transform
Bronze â†’ Silver (Parquet)             Bronze â†’ Silver â†’ Gold (BigQuery)
â”‚                                        â”‚
â–¼                                        â–¼
PostgreSQL Star Schema                BigQuery Star Schema (1TB/mo free)
â”‚                                        â”‚
â–¼                                        â–¼
Apache Airflow DAG                    Airflow on GCP e2-micro VM
(Dockerized, local scheduler)         (Always Free, ~$0/mo)
## Tech Stack

| Layer | Local (Phase 1) | Cloud (Phase 2) |
|---|---|---|
| Ingestion | Python + requests | Python + Cloud Functions |
| Storage | Local filesystem | GCS Bucket |
| Transform | PySpark 3.5 (local mode) | PySpark / BigQuery SQL |
| Warehouse | PostgreSQL 15 | BigQuery |
| Orchestration | Apache Airflow 2.9 | Airflow on e2-micro VM |
| Containerisation | Docker + Compose | Cloud Run / GCE |

## Schema Design (Star Schema)
dim_time â”€â”€â”€â”€â”€â”€â”
â”œâ”€â”€â–º fact_generation
dim_source â”€â”€â”€â”€â”˜
- `fact_generation`: generation_mw, carbon_intensity per source per day
- `dim_time`: date, year, month, day
- `dim_source`: wind, gas, coal, hydro, solar, interconnector

## Key Engineering Decisions

- **Rejected Cloud Composer** (~$300/mo minimum) in favour of self-managed Airflow on GCP Always-Free e2-micro VM
- **Medallion architecture**: raw NDJSON â†’ Parquet (Silver) â†’ PostgreSQL/BigQuery (Gold)
- **Idempotent loads**: `INSERT ... ON CONFLICT DO UPDATE` prevents duplicate rows on DAG reruns
- **Explicit PySpark schema**: never infer schema on production pipelines â€” catches upstream API changes immediately
- **Local-mode Spark**: `local[*]` in Phase 1 keeps infrastructure simple; same transform code runs on cluster in Phase 2 with zero changes

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
| Spark Master UI | http://localhost:8081 | â€” |
| PostgreSQL | localhost:5432 | airflow / airflow |

### Trigger a pipeline run
1. Open http://localhost:8080
2. Enable the `ingest_grid_data` DAG
3. Click Trigger DAG
4. Watch: fetch_grid_data â†’ bronze_to_silver â†’ silver_to_gold

### Verify data in Postgres
```sql
SELECT dt.date, ds.source_name, fg.generation_mw, fg.carbon_intensity
FROM fact_generation fg
JOIN dim_time dt ON fg.time_id = dt.time_id
JOIN dim_source ds ON fg.source_id = ds.source_id
ORDER BY dt.date, ds.source_name;
```

## Repository Structure
ireland-grid-carbon-tracker/
â”œâ”€â”€ dags/
â”‚   â””â”€â”€ dags_ingest.py          # Airflow DAG: fetch â†’ transform â†’ load
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ ingestion/
â”‚   â”‚   â””â”€â”€ fetch_eirgrid.py    # Data ingestion (synthetic generator)
â”‚   â””â”€â”€ transform/
â”‚       â”œâ”€â”€ bronze_to_silver.py # PySpark: NDJSON â†’ Parquet
â”‚       â””â”€â”€ silver_to_gold.py   # Pandas: Parquet â†’ PostgreSQL upsert
â”œâ”€â”€ sql/
â”‚   â””â”€â”€ ddl/
â”‚       â””â”€â”€ schema.sql          # Star schema DDL
â”œâ”€â”€ docker/
â”‚   â””â”€â”€ airflow/
â”‚       â””â”€â”€ Dockerfile          # Custom Airflow image with Java + PySpark
â””â”€â”€ docker-compose.yml          # Full local stack definition
## Profile Summary (for LinkedIn/CV)

- Built and migrated a renewable-energy analytics pipeline from a fully Dockerized local stack to a GCP Always-Free architecture at $0 ongoing cost
- Implemented Medallion architecture (Bronze/Silver/Gold) with PySpark 3.5 and Apache Airflow 2.9 orchestration
- Enforced idempotent loads via PostgreSQL upsert patterns, preventing data duplication on pipeline reruns
- Rejected Cloud Composer (~$300/mo) in favour of cost-aware architecture using GCP Always-Free e2-micro VM

## Phase 2: GCP Migration (In Progress)

- [ ] GCS bucket for raw zone
- [ ] BigQuery star schema
- [ ] Airflow on e2-micro Always-Free VM
- [ ] Cloud Function for ingestion trigger
- [ ] Cost guardrail CI check (BigQuery dry-run)
- [ ] GitHub Actions CI/CD pipeline