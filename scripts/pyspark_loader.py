import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession  # type: ignore

# 1. Load environment variables from .env file
load_dotenv()

# Retrieve credentials & paths with fallback defaults
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "olist")

SPARK_JARS_PATH = os.getenv("SPARK_JARS_PATH", "./postgresql-42.7.12.jar")
RAW_DIR = os.getenv("RAW_DATA_DIR", "./data/raw")

# Construct JDBC Database URL dynamically
DB_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
PROPS = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

# 2. Initialize Spark Session using loaded jar path
spark = SparkSession.builder \
    .appName("OlistRawIngestion") \
    .config("spark.jars", SPARK_JARS_PATH) \
    .getOrCreate()

print(f"Starting PySpark Raw Data Ingestion into PostgreSQL ({DB_HOST}:{DB_PORT}/{DB_NAME})...")

# Verify raw directory exists
if not os.path.exists(RAW_DIR):
    raise FileNotFoundError(f"Target directory {RAW_DIR} does not exist!")

# 3. Iterate through all CSV files in raw landing directory
for file_name in os.listdir(RAW_DIR):
    if file_name.endswith(".csv"):
        file_path = os.path.join(RAW_DIR, file_name)
        
        # Clean up table name: 'olist_customers_dataset.csv' -> 'raw_customers'
        clean_name = (
            file_name.replace(".csv", "")
                     .replace("olist_", "")
                     .replace("_dataset", "")
        )
        table_name = f"raw_{clean_name}"
        
        print(f"Reading {file_name} via PySpark...")
        
        # Read CSV with header and inferSchema enabled
        df = spark.read.csv(file_path, header=True, inferSchema=True)
        
        print(f"Writing {df.count()} rows -> PostgreSQL schema 'raw.{table_name}'...")
        
        # Write to PostgreSQL 'raw' schema
        df.write.jdbc(
            url=DB_URL, 
            table=f"raw.{table_name}", 
            mode="overwrite", 
            properties=PROPS
        )

print("[/] PySpark Raw Ingestion Complete.")