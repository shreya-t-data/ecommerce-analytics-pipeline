from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "shreya",
    "retries": 1,
}

with DAG(
    dag_id="ecommerce_pipeline",
    default_args=default_args,
    description="Ingest Olist CSVs, transform with dbt, run data quality tests",
    schedule=None, #manual trigger only, for now - no need for a schedule while learning
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ecommerce", "dbt"],
) as dag:

    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command="cd /opt/airflow && python src/load/load_raw_data.py"
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt/ecommerce_pipeline && "
            "dbt run --profiles-dir /opt/airflow/.dbt "
            "--log-path /tmp/dbt_logs --target-path /tmp/dbt_target"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/dbt/ecommerce_pipeline && "
            "dbt test --profiles-dir /opt/airflow/.dbt "
            "--log-path /tmp/dbt_logs --target-path /tmp/dbt_target"
        ),
    )

    load_raw_data >> dbt_run >> dbt_test