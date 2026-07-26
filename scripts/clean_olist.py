import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from cleaners import (
    clean_customers,
    clean_orders,
    clean_order_items,
    clean_order_payments,
    clean_order_reviews,
    clean_products,
    clean_product_category_translation,
    clean_sellers,
    clean_geolocation,
)

load_dotenv()

# Database Credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
RAW_SCHEMA = os.getenv("DB_RAW_DATA_TABLE")         # Source/Reference Schema
CLEANED_SCHEMA = os.getenv("DB_CLEANED_TABLE")      # Target Connection Schema

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)


def run_pipeline():
    # AUTOMATICALLY CREATE TARGET SCHEMA IF NOT EXISTS
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {CLEANED_SCHEMA};"))
        conn.commit()

    print(f"Connected to Database: {DB_NAME}")
    print(f"Pipeline: Reading from '{RAW_SCHEMA}' schema ➔ Writing to '{CLEANED_SCHEMA}' schema\n")

    # Step A: Clean translations table first
    print(f"Processing: {RAW_SCHEMA}.raw_product_category_name_translation...")
    
    # READ FROM REFERENCE SCHEMA (RAW)
    raw_trans = pd.read_sql(f"SELECT * FROM {RAW_SCHEMA}.raw_product_category_name_translation", engine)
    clean_trans_df = clean_product_category_translation(raw_trans)
    
    # WRITE TO TARGET SCHEMA (STAGING)
    clean_trans_df.to_sql(
        name="clnd_product_category_translation",
        con=engine,
        schema=CLEANED_SCHEMA, # <-- Target schema assigned here
        if_exists="replace",
        index=False
    )

    # Step B: Pipeline mapping for standard tables
    pipeline_config = [
        ("raw_customers", "clnd_customers", clean_customers),
        ("raw_orders", "clnd_orders", clean_orders),
        ("raw_order_items", "clnd_order_items", clean_order_items),
        ("raw_sellers", "clnd_sellers", clean_sellers),
        ("raw_order_payments", "clnd_payments", clean_order_payments),
        ("raw_order_reviews", "clnd_reviews", clean_order_reviews),
        ("raw_geolocation", "clnd_geolocation", clean_geolocation),
    ]

    for raw_tbl, clnd_tbl, clean_fn in pipeline_config:
        print(f"📦 Processing: '{RAW_SCHEMA}.{raw_tbl}' -> '{CLEANED_SCHEMA}.{clnd_tbl}'...")
        try:
            # READ from raw schema
            raw_df = pd.read_sql(f"SELECT * FROM {RAW_SCHEMA}.{raw_tbl}", engine)
            cleaned_df = clean_fn(raw_df)
            
            # WRITE to staging schema
            cleaned_df.to_sql(
                name=clnd_tbl,
                con=engine,
                schema=CLEANED_SCHEMA, # <-- Target schema assigned here
                if_exists="replace",
                index=False
            )
            print(f"✅ Wrote {len(cleaned_df)} rows to '{CLEANED_SCHEMA}.{clnd_tbl}'.\n")
        except Exception as e:
            print(f"❌ Failed processing '{raw_tbl}': {str(e)}\n")

    # Step C: Clean products passing translated categories lookup
    print(f"📦 Processing: {RAW_SCHEMA}.raw_products -> {CLEANED_SCHEMA}.clnd_products...")
    try:
        raw_products = pd.read_sql(f"SELECT * FROM {RAW_SCHEMA}.raw_products", engine)
        clean_prod_df = clean_products(raw_products, clean_trans_df)
        clean_prod_df.to_sql(
            name="clnd_products",
            con=engine,
            schema=CLEANED_SCHEMA, # <-- Target schema assigned here
            if_exists="replace",
            index=False
        )
        print(f"✅ Wrote {len(clean_prod_df)} rows to '{CLEANED_SCHEMA}.clnd_products'.")
    except Exception as e:
        print(f"❌ Failed processing 'raw_products': {str(e)}")


if __name__ == "__main__":
    run_pipeline()