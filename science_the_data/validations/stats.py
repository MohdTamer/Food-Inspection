"""
stats.py
--------
Compute basic dataset statistics and return them as plain dicts.
Nothing is printed here — the report writer handles output.
"""

from __future__ import annotations

import pandas as pd


# ── Types ─────────────────────────────────────────────────────────────────────

StatsReport = dict  # typed alias for readability


# ── Public API ────────────────────────────────────────────────────────────────

def compute_basic_stats(df: pd.DataFrame) -> StatsReport:
    """
    Return a dict with shape, dtypes, missing-value counts, and duplicate counts.

    Returns
    -------
    {
        "n_rows": int,
        "n_cols": int,
        "dtypes": {col: dtype_str, ...},
        "missing": {col: {"count": int, "pct": float}, ...},   # only cols with missing
        "full_duplicates": int,
        "id_duplicates":   int,   # duplicate "Inspection ID" rows
    }
    """
    missing_raw = df.isnull().sum()
    missing_pct = (missing_raw / len(df) * 100).round(2)

    missing = {
        col: {"count": int(missing_raw[col]), "pct": float(missing_pct[col])}
        for col in df.columns
        if missing_raw[col] > 0
    }

    return {
        "n_rows":          int(df.shape[0]),
        "n_cols":          int(df.shape[1]),
        "dtypes":          {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing":         missing,
        "full_duplicates": int(df.duplicated().sum()),
        "id_duplicates":   int(df.duplicated(subset=["Inspection ID"]).sum()),
    }