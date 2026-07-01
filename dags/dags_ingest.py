from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/opt/airflow/src')

from ingestion.fetch_eirgrid import fetch_and_save
from transform.bronze_to_silver import run_transform
from transform.silver_to_gold import load_to_postgres

with DAG(
    dag_id="ingest_grid_data",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_grid_data",
        python_callable=fetch_and_save,
    )

    transform_task = PythonOperator(
        task_id="bronze_to_silver",
        python_callable=run_transform,
        op_args=["{{ ds }}"],
    )

    load_task = PythonOperator(
        task_id="silver_to_gold",
        python_callable=load_to_postgres,
        op_args=["{{ ds }}"],
    )

    fetch_task >> transform_task >> load_task