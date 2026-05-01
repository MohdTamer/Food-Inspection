from __future__ import annotations

import pandas as pd

def quarantine_missing_results(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "Results" not in df.columns:
        return df.copy(), pd.DataFrame(columns=df.columns)

    results = df["Results"].astype("string").str.strip()
    quarantine_mask = results.isna() | results.eq("")

    quarantined = df.loc[quarantine_mask].copy()
    quarantined["quarantine_reason"] = "missing_results"

    clean = df.loc[~quarantine_mask].copy()
    clean["Results"] = results.loc[~quarantine_mask]

    return clean, quarantined