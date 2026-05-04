from __future__ import annotations

import pandas as pd
from loguru import logger


def _fail_rate_last_3(series: pd.Series) -> pd.Series:
    return series.shift(1).rolling(window=3, min_periods=1).mean()


def add_inspection_history_features(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute lag / rolling features that require cross-split temporal ordering.

    All three splits are combined before computing features so that a business
    that straddles the train/val boundary gets correct lag values in val.
    Null-fill statistics are derived from train only to prevent leakage.

    New columns added
    -----------------
    days_since_last_inspection : float
        Calendar days between the current and previous inspection for the same
        licence.  First inspection per licence is filled with the train median.
    prev_inspection_result : float
        Binary result (0/1) of the immediately preceding inspection.
        First inspection per licence is filled with the train mean.
    fail_rate_last_3 : float
        Rolling mean of the previous 3 inspection results (shift(1) ensures the
        current row is excluded).  Filled with the train mean for cold-start rows.

    Parameters
    ----------
    train, val, test:
        DataFrames that must contain ``License #``, ``Inspection Date``
        (datetime-like), and ``Results`` (binary int) columns.

    Returns
    -------
    train, val, test with the three new feature columns appended.
    """
    train = train.copy()
    val   = val.copy()
    test  = test.copy()

    train["_split"] = "train"
    val["_split"]   = "val"
    test["_split"]  = "test"

    combined = (
        pd.concat([train, val, test])
        .sort_values(["License #", "Inspection Date"])
        .reset_index(drop=True)
    )

    combined["days_since_last_inspection"] = (
        combined.groupby("License #")["Inspection Date"].diff().dt.days
    )
    combined["prev_inspection_result"] = (
        combined.groupby("License #")["Results"].shift(1)
    )
    combined["fail_rate_last_3"] = (
        combined.groupby("License #")["Results"].transform(_fail_rate_last_3)
    )

    # Null-fill statistics — train split only
    train_mask = combined["_split"] == "train"
    median_gap = combined.loc[train_mask, "days_since_last_inspection"].median()
    prev_mean  = combined.loc[train_mask, "prev_inspection_result"].mean()
    fail_mean  = combined.loc[train_mask, "fail_rate_last_3"].mean()

    combined["days_since_last_inspection"] = combined["days_since_last_inspection"].fillna(median_gap)
    combined["prev_inspection_result"]     = combined["prev_inspection_result"].fillna(prev_mean)
    combined["fail_rate_last_3"]           = combined["fail_rate_last_3"].fillna(fail_mean)

    train = combined[combined["_split"] == "train"].drop(columns="_split").reset_index(drop=True)
    val   = combined[combined["_split"] == "val"].drop(columns="_split").reset_index(drop=True)
    test  = combined[combined["_split"] == "test"].drop(columns="_split").reset_index(drop=True)

    logger.info(
        "Inspection history features added — "
        "median_gap={:.0f}  prev_mean={:.4f}  fail_mean={:.4f}",
        median_gap,
        prev_mean,
        fail_mean,
    )

    return train, val, test