import pandas as pd

def clean_order_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Applies cleaning transformations to raw_order_reviews."""
    df = df.copy()

    df = df.drop_duplicates(subset=["review_id", "order_id"])
    
    # 1. Convert to datetime FIRST (invalid dates become NaT)
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")

    # 2. Drop NAs/NaTs AFTER conversion so NaT doesn't reach Postgres
    df = df.dropna(subset=[
        "review_id", 
        "order_id", 
        "review_score", 
        "review_creation_date", 
        "review_answer_timestamp"
    ])

    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").astype("Int64")
    df = df[df["review_score"].between(1, 5)]

    df["review_comment_title"] = df["review_comment_title"].fillna("No Title").astype(str).str.strip()
    df["review_comment_message"] = df["review_comment_message"].fillna("No Comment").astype(str).str.strip()

    return df