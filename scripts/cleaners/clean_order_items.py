import pandas as pd

def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_order_items."""
    df = df.copy()

    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"])

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce")

    df["price"] = df["price"].apply(lambda x: max(0.00, x))
    df["freight_value"] = df["freight_value"].apply(lambda x: max(0.00, x))

    if "shipping_limit_date" in df.columns:
        df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")

    return df