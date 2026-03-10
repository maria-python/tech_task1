from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.api.ecb_client import fetch_currency_rates
from src.processing.transform import transform_currency_data


def maintenance_task(**context):
    dag_run = context.get("dag_run")

    conf = dag_run.conf if dag_run and dag_run.conf else {}

    start_date = conf.get("start_date", "2024-01-01")
    end_date = conf.get("end_date", "2024-01-10")

    raw_data = fetch_currency_rates(start_date=start_date, end_date=end_date)
    transformed_data = transform_currency_data(raw_data)

    print(f"Maintenance DAG completed successfully. Prepared {len(transformed_data)} rows.")
    print(transformed_data)


with DAG(
    dag_id="maintenance_currency_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["maintenance", "currency"],
) as dag:
    run_maintenance = PythonOperator(
        task_id="fetch_transform_currency_data",
        python_callable=maintenance_task,
    )