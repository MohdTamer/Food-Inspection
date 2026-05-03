from __future__ import annotations

import pandas as pd
from loguru import logger

DATE_COLS = ["Inspection Date", "LICENSE TERM START DATE", "LICENSE TERM EXPIRATION DATE"]

RISK_MAP = {
    "High":    3,
    "Medium":  2,
    "Low":     1,
    "Unknown": 3,  # mode imputation
}


def encode_risk(df_train: pd.DataFrame, df_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_test  = df_test.copy()

    for label, df in [("train", df_train), ("test", df_test)]:
        unexpected = set(df["Risk"].dropna().unique()) - set(RISK_MAP.keys())
        if unexpected:
            logger.warning("Unexpected Risk values in {}: {}", label, unexpected)

    df_train["Risk"] = df_train["Risk"].map(RISK_MAP)
    df_test["Risk"]  = df_test["Risk"].map(RISK_MAP)

    logger.info("Risk encoded — train value counts: {}", df_train["Risk"].value_counts().to_dict())

    return df_train, df_test


def parse_dates(df_train: pd.DataFrame, df_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_test  = df_test.copy()

    for col in DATE_COLS:
        if col not in df_train.columns:
            logger.warning("Date column '{}' not found — skipping.", col)
            continue

        df_train[col] = pd.to_datetime(df_train[col], errors="coerce")
        df_test[col]  = pd.to_datetime(df_test[col],  errors="coerce")

        logger.info(
            "{}: dtype={}, nulls_train={}, nulls_test={}",
            col,
            df_train[col].dtype,
            df_train[col].isna().sum(),
            df_test[col].isna().sum(),
        )

    return df_train, df_test


def engineer_license_expiry(df_train: pd.DataFrame, df_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_test  = df_test.copy()

    for df in [df_train, df_test]:
        df["days_to_license_expiry"] = (
            pd.to_datetime(df["LICENSE TERM EXPIRATION DATE"]) - pd.to_datetime(df["Inspection Date"])
        ).dt.days
        df["license_expiry_missing"] = df["days_to_license_expiry"].isna().astype(int)

    median_expiry = df_train["days_to_license_expiry"].median()
    logger.info("Median days to license expiry (train): {:.0f} days", median_expiry)

    df_train["days_to_license_expiry"] = df_train["days_to_license_expiry"].fillna(median_expiry)
    df_test["days_to_license_expiry"]  = df_test["days_to_license_expiry"].fillna(median_expiry)

    logger.info(
        "Remaining nulls — train: {}, test: {}",
        df_train["days_to_license_expiry"].isna().sum(),
        df_test["days_to_license_expiry"].isna().sum(),
    )

    return df_train, df_test


def apply_feature_engineering(df_train: pd.DataFrame, df_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_train, df_test = encode_risk(df_train, df_test)
    df_train, df_test = parse_dates(df_train, df_test)
    df_train, df_test = engineer_license_expiry(df_train, df_test)
    return df_train, df_test