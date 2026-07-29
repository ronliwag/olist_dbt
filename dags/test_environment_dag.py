from datetime import datetime
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

DBT_PROJECT_PATH = Path("/usr/local/airflow/include/dbt")

with DAG(
    dag_id="00_test_environment_and_connection",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["test", "setup"],
) as dag:

    # 1. Test Java Installation
    test_java = BashOperator(
        task_id="check_java_version",
        bash_command="java -version",
    )

    # 2. Check File & Folder Visibility inside Container
    test_files = BashOperator(
        task_id="check_include_directory_files",
        bash_command="""
            echo "=== Checking Include Directory ==="
            ls -la /usr/local/airflow/include
        """,
    )

    # 3. Test Database Connection
    test_db_conn = SQLExecuteQueryOperator(
        task_id="check_postgres_connection",
        conn_id="postgres_default",
        sql="""
            SELECT version();
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE SCHEMA IF NOT EXISTS cleaned;
        """,
    )

    [test_java, test_files, test_db_conn]