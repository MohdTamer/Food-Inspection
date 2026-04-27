from __future__ import annotations

import pandas as pd


def quarantine_missing_results(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits df into (clean, quarantined) on the Results column.

    Quarantine criteria: Results is null or empty string.
    Rows with valid Results values — including "Not Ready", "Out of Business",
    "Business Not Located", and "No Entry" — are retained in the clean set.
    Whether those outcomes are useful for a specific model is a modelling
    decision and does not belong here.

    Returns
    -------
    clean       : rows with a non-empty Results value
    quarantined : rows without one, with a quarantine_reason column added
    """
    if "Results" not in df.columns:
        return df.copy(), pd.DataFrame(columns=df.columns)

    results = df["Results"].astype("string").str.strip()
    quarantine_mask = results.isna() | results.eq("")

    quarantined = df.loc[quarantine_mask].copy()
    quarantined["quarantine_reason"] = "missing_results"

    clean = df.loc[~quarantine_mask].copy()
    clean["Results"] = results.loc[~quarantine_mask]

    return clean, quarantined