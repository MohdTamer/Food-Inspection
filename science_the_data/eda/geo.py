from __future__ import annotations

import pandas as pd


def geo_sample(df: pd.DataFrame, n: int = 5000, seed: int = 42) -> pd.DataFrame:
    required = {"Latitude", "Longitude"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    cols = [c for c in ["Latitude", "Longitude", "Results"] if c in df.columns]
    geo = df[cols].dropna(subset=["Latitude", "Longitude"])
    return geo.sample(min(n, len(geo)), random_state=seed).reset_index(drop=True)


def fail_rate_by_community(df: pd.DataFrame) -> pd.DataFrame:
    if "COMMUNITY AREA NAME" not in df.columns or "Results" not in df.columns:
        return pd.DataFrame()

    return (
        df.groupby("COMMUNITY AREA NAME")["Results"]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="fail_rate")
    )