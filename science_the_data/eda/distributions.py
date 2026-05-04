from __future__ import annotations

import pandas as pd


def class_balance(df: pd.DataFrame, target: str = "Results") -> dict:
    counts = df[target].value_counts()
    total = len(df)
    return {
        "counts": counts.to_dict(),
        "pct": (counts / total * 100).round(2).to_dict(),
    }


def cardinality_summary(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "unique_values": df.nunique(),
        "dtype": df.dtypes
    }).sort_values("unique_values", ascending=False)

def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    stats = df.select_dtypes(include="number").describe().T
    stats['skew'] = df.select_dtypes(include="number").skew()
    return stats


def top_facility_types(df: pd.DataFrame, n: int = 10) -> pd.Series:
    if "Facility Type" in df.columns:
        return df["Facility Type"].value_counts().head(n)
    elif "facility_type_encoded" in df.columns:
        return df["facility_type_encoded"].value_counts().head(n)
    return pd.Series(dtype=int)


def risk_distribution(df: pd.DataFrame) -> pd.Series:
    if "Risk" in df.columns:
        return df["Risk"].value_counts().sort_index()
    return pd.Series(dtype=int)


def inspection_type_distribution(df: pd.DataFrame) -> pd.Series:
    if "Inspection Type" in df.columns:
        return df["Inspection Type"].value_counts()
    elif "inspection_type_encoded" in df.columns:
        return df["inspection_type_encoded"].value_counts()
    return pd.Series(dtype=int)
