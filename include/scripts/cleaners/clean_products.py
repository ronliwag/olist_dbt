import pandas as pd

def clean_products(df: pd.DataFrame, translation_df: pd.DataFrame = None) -> pd.DataFrame:
    """Applies cleaning transformations to raw_products."""
    df = df.copy()

    df = df.drop_duplicates(subset=["product_id"])
    df = df.dropna(subset=["product_id", "product_category_name", "product_name_lenght"])

    df["product_category_name"] = df["product_category_name"].fillna("unassigned")

    if translation_df is not None:
        df = df.merge(translation_df, on="product_category_name", how="left")
        df["product_category_name_english"] = df["product_category_name_english"].fillna("unassigned")

    int_numeric_cols = ["product_photo_qty", "product_name_lenght", "product_description_lenght"]
    for col in int_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    double_numeric_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    for col in double_numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.00)

    return df