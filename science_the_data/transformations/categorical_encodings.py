from __future__ import annotations

from loguru import logger
import pandas as pd

APP_TYPE_MAP: dict[str, int] = {
    "ISSUE": 0,
    "RENEW": 1,
    "C_LOC": 2,
    "C_EXPA": 2,
    "C_CAPA": 2,
    "C_SBA": 2,
}

NO_LONGER_NEEDED = [
    "Inspection ID",
    "License #",
    "Zip",
    "Longitude",
    "Latitude",
    "Violations",
    "license_matched",
    "Inspection Type",
    "Facility Type",
    "COMMUNITY AREA NAME",
    "LICENSE DESCRIPTION",
    "LICENSE STATUS",
    "APPLICATION TYPE",
    "Inspection Date",
    "violations_recorded",
]


def encode_categorical_features(
    train: pd.DataFrame,
    val: pd.DataFrame,
    test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply target encoding, ordinal mapping, binary flags, and drop raw columns.

    All encoding statistics (fail rates, global mean) are fitted on *train* only
    and then applied to val and test to prevent leakage.

    New columns added
    -----------------
    inspection_type_encoded : float
        Mean failure rate per ``Inspection Type`` (fitted on train).
    facility_type_encoded : float
        Mean failure rate per ``Facility Type`` (fitted on train).
    is_revoked : int  {0, 1}
        1 when ``LICENSE STATUS`` == 'REV'.
    application_type_encoded : int  {0, 1, 2}
        Ordinal encoding of ``APPLICATION TYPE`` via ``APP_TYPE_MAP``; unknown
        values default to 1 (renewal).

    Columns removed
    ---------------
    All columns listed in ``NO_LONGER_NEEDED`` that are present in the frame.

    Parameters
    ----------
    train, val, test:
        DataFrames that must contain the raw columns referenced above.

    Returns
    -------
    train, val, test with encoded columns appended and raw columns removed.
    """
    train = train.copy()
    val = val.copy()
    test = test.copy()

    global_mean = train["Results"].mean()

    insp_fail_rate = train.groupby("Inspection Type")["Results"].mean()
    for df in (train, val, test):
        df["inspection_type_encoded"] = (
            df["Inspection Type"].map(insp_fail_rate).fillna(global_mean)
        )

    logger.info(
        "inspection_type_encoded — nulls: train={}, val={}, test={}",
        train["inspection_type_encoded"].isna().sum(),
        val["inspection_type_encoded"].isna().sum(),
        test["inspection_type_encoded"].isna().sum(),
    )

    facility_fail_rate = train.groupby("Facility Type")["Results"].mean()
    for df in (train, val, test):
        df["facility_type_encoded"] = (
            df["Facility Type"].map(facility_fail_rate).fillna(global_mean)
        )

    logger.info(
        "facility_type_encoded — nulls: train={}, val={}, test={}",
        train["facility_type_encoded"].isna().sum(),
        val["facility_type_encoded"].isna().sum(),
        test["facility_type_encoded"].isna().sum(),
    )

    for df in (train, val, test):
        df["is_revoked"] = (df["LICENSE STATUS"] == "REV").astype(int)

    for df in (train, val, test):
        df["application_type_encoded"] = df["APPLICATION TYPE"].map(APP_TYPE_MAP).fillna(1)

    cols_to_drop = [c for c in NO_LONGER_NEEDED if c in train.columns]
    skipped = [c for c in NO_LONGER_NEEDED if c not in train.columns]

    if skipped:
        logger.warning(
            "encode_categorical_features — {} column(s) not found, skipped: {}",
            len(skipped),
            skipped,
        )

    train = train.drop(columns=cols_to_drop)
    val = val.drop(columns=cols_to_drop)
    test = test.drop(columns=cols_to_drop)

    logger.info(
        "Categorical encodings complete — dropped {} raw column(s) | remaining columns: {}",
        len(cols_to_drop),
        train.columns.tolist(),
    )

    return train, val, test
