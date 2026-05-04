from __future__ import annotations

import pandas as pd
from loguru import logger

PwC_THRESHOLD = 4
TARGET_MAP = { "Pass": 0, "Fail": 1 }


def count_violations(series: pd.Series) -> pd.Series:
    return (
        series
        .fillna("")
        .apply(lambda x: len(x.split(" | ")) if x.strip() else 0)
    )


def binarize_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["violation_count"] = count_violations(df["Violations"])

    binary   = df["Results"].map(TARGET_MAP)
    pwc_mask = df["Results"] == "Pass w/ Conditions"
    binary[pwc_mask] = (df.loc[pwc_mask, "violation_count"] >= PwC_THRESHOLD).astype(int)

    assert binary.isna().sum() == 0, "Unmapped values in 'Results'!"

    df["Results"] = binary.astype(int)
    df = df.drop(columns=["violation_count"])

    logger.info(
        "Binarization complete (PwC threshold = {}) — class counts: {}",
        PwC_THRESHOLD,
        df["Results"].value_counts().to_dict(),
    )

    return df