import pandas as pd

def clean_product_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_product_category_name_translation."""
    df = df.copy()

    df = df.drop_duplicates(subset=["product_category_name"])
    df = df.dropna(subset=["product_category_name", "product_category_name_english"])

    df["product_category_name"] = df["product_category_name"].astype(str).str.strip().str.lower()
    df["product_category_name_english"] = df["product_category_name_english"].astype(str).str.strip().str.lower()

    return df