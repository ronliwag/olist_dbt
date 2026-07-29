#!/usr/bin/env bash
set -e 

# 1. Fallback environment loading if running outside Airflow execution
if [ -f /usr/local/airflow/.env ]; then
    export $(grep -v '^#' /usr/local/airflow/.env | xargs)
fi

# 2. Use environment variables with default fallbacks
OUTPUT_DIR="${RAW_DATA_DIR:-/usr/local/airflow/include/data/raw}"
JAR_PATH="${SPARK_JARS_PATH:-/usr/local/airflow/include/jars/postgresql-42.7.12.jar}"
JARS_DIR="$(dirname "$JAR_PATH")"
DATASET_NAME="olistbr/brazilian-ecommerce"

# Ensure directories exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$JARS_DIR"

# 3. Download PostgreSQL JDBC Driver JAR (if not present)
if [ ! -f "$JAR_PATH" ]; then
    echo "[$(date)] Downloading PostgreSQL JDBC Driver..."
    curl -L "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.12/postgresql-42.7.12.jar" -o "$JAR_PATH"
    echo "[$(date)] Downloaded JDBC JAR to $JAR_PATH"
else
    echo "[$(date)] PostgreSQL JDBC JAR already exists. Skipping download."
fi

# 4. Verify Kaggle Credentials
if [ -z "$KAGGLE_USERNAME" ] || [ -z "$KAGGLE_KEY" ]; then
    echo "ERROR: Kaggle credentials (KAGGLE_USERNAME / KAGGLE_KEY) are missing!"
    exit 1
fi

# 5. Download and unzip dataset via Kaggle CLI
echo "[$(date)] Initiating dataset download from Kaggle ($DATASET_NAME)..."
kaggle datasets download -d "$DATASET_NAME" -p "$OUTPUT_DIR" --unzip

# 6. Validation Check
FILE_COUNT=$(ls -1 "$OUTPUT_DIR"/*.csv 2>/dev/null | wc -l)
echo "[$(date)] Ingestion complete: $FILE_COUNT CSV files extracted into $OUTPUT_DIR"