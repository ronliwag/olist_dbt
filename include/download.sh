#!/usr/bin/env bash
# Make sure to run: chmod +x include/download.sh
set -e 

# 1. Load credentials from .env file if present
if [ -f /usr/local/airflow/.env ]; then
    export $(grep -v '^#' /usr/local/airflow/.env | xargs)
fi

# Set Container Paths
OUTPUT_DIR="${RAW_DATA_DIR:-/usr/local/airflow/include/data/raw}"
JAR_PATH="${SPARK_JARS_PATH:-/usr/local/airflow/include/postgresql-42.7.12.jar}"
DATASET_NAME="olistbr/brazilian-ecommerce"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$(dirname "$JAR_PATH")"

# 2. Download PostgreSQL JDBC Driver JAR (if not present)
if [ ! -f "$JAR_PATH" ]; then
    echo "[$(date)] Downloading PostgreSQL JDBC Driver..."
    curl -sSL -o "$JAR_PATH" "https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.12/postgresql-42.7.12.jar"
    echo "[$(date)] Downloaded JDBC JAR to $JAR_PATH"
else
    echo "[$(date)] PostgreSQL JDBC JAR already exists. Skipping download."
fi

# 3. Allow command line arguments to override credentials if passed
if [ -n "$1" ] && [ -n "$2" ]; then
    export KAGGLE_USERNAME="$1"
    export KAGGLE_KEY="$2"
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