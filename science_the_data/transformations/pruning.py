from __future__ import annotations

from loguru import logger
import pandas as pd

# High-cardinality columns that add noise without predictive value
NOISE_COLS = ["DBA Name", "AKA Name", "Address"]

# Constant / near-constant flag columns (low variance, no signal)
FLAG_COLS = [
    "flag_non_il_state",
    "flag_longitude_outside_typical_range",
    "flag_non_chicago_city",
]

# Raw date columns — features have already been extracted upstream
RAW_DATE_COLS = ["LICENSE TERM START DATE", "LICENSE TERM EXPIRATION DATE"]

PRUNE_COLS = NOISE_COLS + FLAG_COLS + RAW_DATE_COLS


def prune_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()

    dropped, skipped = [], []
    for col in PRUNE_COLS:
        if col in df.columns:
            dropped.append(col)
        else:
            skipped.append(col)

    if skipped:
        logger.warning("Pruning — {} column(s) not found, skipped: {}", len(skipped), skipped)

    df = df.drop(columns=dropped)

    logger.info(
        "Pruning complete — dropped {} column(s): {}  |  remaining columns: {}",
        len(dropped),
        dropped,
        df.shape[1],
    )

    return df, dropped
