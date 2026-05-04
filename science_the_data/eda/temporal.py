from __future__ import annotations

import pandas as pd


def inspections_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.Series:
    if "Inspection Date" not in df.columns:
        return pd.Series(dtype=int)
    dates = pd.to_datetime(df["Inspection Date"], errors="coerce")
    return dates.dropna().dt.to_period(freq).value_counts().sort_index()


def fail_rate_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.Series:
    if "Inspection Date" not in df.columns or "Results" not in df.columns:
        return pd.Series(dtype=float)
    tmp = df[["Inspection Date", "Results"]].copy()
    tmp["Inspection Date"] = pd.to_datetime(tmp["Inspection Date"], errors="coerce")
    tmp = tmp.dropna(subset=["Inspection Date"])
    tmp["period"] = tmp["Inspection Date"].dt.to_period(freq)
    return tmp.groupby("period")["Results"].mean().rename("fail_rate")