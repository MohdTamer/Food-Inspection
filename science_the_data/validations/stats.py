from __future__ import annotations

import pandas as pd

StatsReport = dict


def compute_basic_stats(df: pd.DataFrame) -> StatsReport:
    missing_raw = df.isnull().sum()
    missing_pct = (missing_raw / len(df) * 100).round(2)

    missing = {
        col: {"count": int(missing_raw[col]), "pct": float(missing_pct[col])}
        for col in df.columns
        if missing_raw[col] > 0
    }

    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing": missing,
        "full_duplicates": int(df.duplicated().sum()),
        "id_duplicates": int(df.duplicated(subset=["Inspection ID"]).sum()),
    }
