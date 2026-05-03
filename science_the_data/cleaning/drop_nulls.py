import pandas as pd


def drop_fully_nulls_columns(df: pd.DataFrame) -> pd.DataFrame:
    all_null_cols = [c for c in df.columns if df[c].isna().all()]
    df_clean = df.drop(columns=all_null_cols)
    return df_clean


def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.drop_duplicates(keep="first")
    return df_clean


def drop_inspection_id_duplication(df: pd.DataFrame) -> pd.DataFrame:
    if "Inspection Date" in df.columns:
        sort_dates = pd.to_datetime(df["Inspection Date"], errors="coerce")
        df = df.assign(_sort_inspection_date=sort_dates)
        df = df.sort_values(
            ["Inspection ID", "_sort_inspection_date"], ascending=[True, False]
        ).drop(columns=["_sort_inspection_date"])

    df = df.drop_duplicates(subset=["Inspection ID"], keep="first")

    return df
