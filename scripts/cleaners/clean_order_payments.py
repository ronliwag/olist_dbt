import pandas as pd

def clean_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_order_payments."""
    df = df.copy()

    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "payment_type", "payment_value", "payment_installments", "payment_sequential"])

    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"], errors="coerce").astype(int)
    df["payment_type"] = df["payment_type"].astype(str).str.strip().str.lower()
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce").apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

    return df