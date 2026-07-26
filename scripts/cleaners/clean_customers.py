import pandas as pd

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_customers."""
    df = df.copy()

    df = df.drop_duplicates(subset=["customer_id", "customer_unique_id"])
    df = df.dropna(subset=["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"])

    # Zero-pad zip code prefix to 5 digits
    df["customer_zip_code_prefix"] = (
        df["customer_zip_code_prefix"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .str.zfill(5)
    )

    df["customer_city"] = df["customer_city"].astype(str).str.strip().str.title()
    df["customer_state"] = df["customer_state"].astype(str).str.strip().str.upper()

    return df