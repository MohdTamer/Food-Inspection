from __future__ import annotations

import pandas as pd


def numeric_correlation(df: pd.DataFrame) -> pd.DataFrame:
    return df.select_dtypes(include="number").corr()


def target_correlation(df: pd.DataFrame, target: str = "Results") -> pd.Series:
    corr = numeric_correlation(df)
    if target not in corr:
        return pd.Series(dtype=float)
    return corr[target].drop(labels=[target]).sort_values(key=abs, ascending=False)