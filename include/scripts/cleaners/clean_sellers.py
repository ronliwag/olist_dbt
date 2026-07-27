import pandas as pd

def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_sellers."""
    df = df.copy()

    df = df.drop_duplicates(subset=["seller_id"])
    df = df.dropna(subset=["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"])

    df["seller_zip_code_prefix"] = (
        df["seller_zip_code_prefix"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .str.zfill(5)
    )

    df["seller_city"] = df["seller_city"].astype(str).str.strip().str.title()
    df["seller_state"] = df["seller_state"].astype(str).str.strip().str.upper()

    return df