from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/opt/airflow/src')

from ingestion.fetch_eirgrid_gcs import fetch_and_upload
from transform.bronze_to_silver import run_transform
from transform.silver_to_bigquery import load_to_bigquery

with DAG(
    dag_id="cloud_grid_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_to_gcs",
        python_callable=fetch_and_upload,
        op_args=["{{ ds }}"],
    )

    transform_task = PythonOperator(
        task_id="bronze_to_silver",
        python_callable=run_transform,
        op_args=["{{ ds }}", "gcs"],
    )

    load_task = PythonOperator(
        task_id="silver_to_bigquery",
        python_callable=load_to_bigquery,
        op_args=["{{ ds }}"],
    )

    fetch_task >> transform_task >> load_task