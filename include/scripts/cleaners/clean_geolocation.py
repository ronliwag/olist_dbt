import pandas as pd

def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_geolocation."""
    df = df.copy()

    df = df.dropna(subset=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"])

    df["geolocation_zip_code_prefix"] = (
        df["geolocation_zip_code_prefix"]
        .astype(str)
        .str.extract(r"(\d+)")[0]
        .str.zfill(5)
    )

    df["geolocation_city"] = df["geolocation_city"].astype(str).str.strip().str.title()
    df["geolocation_state"] = df["geolocation_state"].astype(str).str.strip().str.upper()

    df = df[df["geolocation_lat"].between(-90, 90)]
    df = df[df["geolocation_lng"].between(-180, 180)]

    return df