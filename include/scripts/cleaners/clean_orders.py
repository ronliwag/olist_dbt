import pandas as pd

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_orders."""
    df = df.copy()

    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "customer_id", "order_status", "order_purchase_timestamp"])

    timestamp_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in timestamp_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["order_status"] = df["order_status"].astype(str).str.strip().str.lower()

    return df