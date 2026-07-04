from google.cloud import bigquery
import pandas as pd

BUCKET_NAME = "ireland-grid-raw-zone"
PROJECT_ID = "ireland-grid-tracker"
DATASET_ID = "ireland_grid"

def load_to_bigquery(run_date: str):
    client = bigquery.Client(project=PROJECT_ID)

    # Read from GCS parquet written by PySpark
    gcs_path = f"gs://{BUCKET_NAME}/silver/{run_date}"
    df = pd.read_parquet(gcs_path)

    if df.empty:
        raise ValueError(f"No silver data found at {gcs_path}")

    print(f"Read {len(df)} rows from silver layer")

    # Load dim_time
    dim_time = df[["date", "year", "month", "day"]].drop_duplicates()
    dim_time["time_id"] = range(1, len(dim_time) + 1)

    time_table = f"{PROJECT_ID}.{DATASET_ID}.dim_time"
    client.load_table_from_dataframe(dim_time, time_table,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )
    ).result()
    print(f"Loaded {len(dim_time)} rows into dim_time")

    # Load dim_source
    dim_source = df[["source_name"]].drop_duplicates()
    dim_source["source_id"] = range(1, len(dim_source) + 1)

    source_table = f"{PROJECT_ID}.{DATASET_ID}.dim_source"
    client.load_table_from_dataframe(dim_source, source_table,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )
    ).result()
    print(f"Loaded {len(dim_source)} rows into dim_source")

    # Load fact_generation
    fact = df.merge(dim_time, on=["date", "year", "month", "day"]) \
             .merge(dim_source, on="source_name")
    fact = fact[["time_id", "source_id", "generation_mw", "carbon_intensity"]]
    fact["fact_id"] = range(1, len(fact) + 1)
    from datetime import datetime as dt
    fact["inserted_at"] = dt.utcnow().isoformat()

    fact_table = f"{PROJECT_ID}.{DATASET_ID}.fact_generation"
    client.load_table_from_dataframe(fact, fact_table,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )
    ).result()
    print(f"Loaded {len(fact)} rows into fact_generation")

if __name__ == "__main__":
    import sys
    load_to_bigquery(sys.argv[1])