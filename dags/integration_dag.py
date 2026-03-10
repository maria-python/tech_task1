from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.api.ecb_client import fetch_currency_rates
from src.processing.transform import transform_currency_data
from src.db.clickhouse_client import insert_batch


def integration_task():
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    raw_data = fetch_currency_rates(start_date=yesterday, end_date=yesterday)
    transformed_data = transform_currency_data(raw_data)

    insert_batch(transformed_data)

    print(f"Integration DAG completed successfully. Inserted {len(transformed_data)} rows.")
    print(transformed_data)


with DAG(
    dag_id="integration_currency_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["integration", "currency"],
) as dag:
    run_integration = PythonOperator(
        task_id="fetch_transform_insert_currency_data",
        python_callable=integration_task,
    )