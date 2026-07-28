from datetime import datetime
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


DBT_PROJECT_PATH = Path("/usr/local/airflow/include/dbt")

default_args = {
    "owner": "data_engineering",
    "retries": 1,
}

with DAG(
    dag_id="olist_end_to_end_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Set to "@daily" or a cron expression when ready
    catchup=False,
    default_args=default_args,
    tags=["olist", "etl", "dbt"],
) as dag:

    # ------------------------------------------------------------------
    # Step 3: Download Raw Files
    # ------------------------------------------------------------------
    download_raw = BashOperator(
        task_id="download_raw_files",
        bash_command="bash /usr/local/airflow/include/download.sh ",
    )

    # ------------------------------------------------------------------
    # Step 4: Run PySpark Loader
    # ------------------------------------------------------------------
    pyspark_load = BashOperator(
        task_id="pyspark_load_raw",
        bash_command="python /usr/local/airflow/include/scripts/pyspark_loader.py",
    )

    # ------------------------------------------------------------------
    # Step 5: Test Raw Schema Loaded
    # ------------------------------------------------------------------
    test_raw_schema = SQLExecuteQueryOperator(
        task_id="test_raw_data_exists",
        conn_id="postgres_default",
        sql="""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'raw' 
              AND table_type = 'BASE TABLE';
        """,
    )

    # ------------------------------------------------------------------
    # Step 6: Trigger Pandas Cleaner Script
    # ------------------------------------------------------------------
    pandas_clean = BashOperator(
        task_id="pandas_clean_data",
        bash_command="python /usr/local/airflow/include/scripts/clean_olist.py",
    )

    # ------------------------------------------------------------------
    # Step 7: Test Cleaned Schema Loaded
    # ------------------------------------------------------------------
    test_cleaned_schema = SQLExecuteQueryOperator(
        task_id="test_cleaned_data_exists",
        conn_id="postgres_default",
        sql="""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'cleaned' 
              AND table_type = 'BASE TABLE';
        """,
    )

    # ------------------------------------------------------------------
    # Step 8: Run dbt Transformations & Tests via Cosmos
    # ------------------------------------------------------------------
    dbt_layer = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=ProfileConfig(
            profile_name="olist",
            target_name="dev",
            profile_mapping=PostgresUserPasswordProfileMapping(
                conn_id="postgres_default",
                profile_args={"schema": "public"},
            ),
        ),
    )

    # ------------------------------------------------------------------
    # Execution Dependencies
    # ------------------------------------------------------------------
    (
        download_raw
        >> pyspark_load
        >> test_raw_schema
        >> pandas_clean
        >> test_cleaned_schema
        >> dbt_layer
    )