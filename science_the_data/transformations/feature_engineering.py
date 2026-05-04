from __future__ import annotations

from loguru import logger
import pandas as pd

DATE_COLS = ["Inspection Date", "LICENSE TERM START DATE", "LICENSE TERM EXPIRATION DATE"]

RISK_MAP = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
    "Unknown": 3,
}


def encode_risk(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_val = df_val.copy()
    df_test = df_test.copy()

    for label, df in [("train", df_train), ("val", df_val), ("test", df_test)]:
        unexpected = set(df["Risk"].dropna().unique()) - set(RISK_MAP.keys())
        if unexpected:
            logger.warning("Unexpected Risk values in {}: {}", label, unexpected)

    df_train["Risk"] = df_train["Risk"].map(RISK_MAP)
    df_val["Risk"] = df_val["Risk"].map(RISK_MAP)
    df_test["Risk"] = df_test["Risk"].map(RISK_MAP)

    logger.info("Risk encoded — train value counts: {}", df_train["Risk"].value_counts().to_dict())

    return df_train, df_val, df_test


def parse_dates(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_val = df_val.copy()
    df_test = df_test.copy()

    for col in DATE_COLS:
        if col not in df_train.columns:
            logger.warning("Date column '{}' not found — skipping.", col)
            continue

        df_train[col] = pd.to_datetime(df_train[col], errors="coerce")
        df_val[col] = pd.to_datetime(df_val[col], errors="coerce")
        df_test[col] = pd.to_datetime(df_test[col], errors="coerce")

        logger.info(
            "{}: dtype={}, nulls_train={}, nulls_val={}, nulls_test={}",
            col,
            df_train[col].dtype,
            df_train[col].isna().sum(),
            df_val[col].isna().sum(),
            df_test[col].isna().sum(),
        )

    return df_train, df_val, df_test


def engineer_license_expiry(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_val = df_val.copy()
    df_test = df_test.copy()

    for df in [df_train, df_val, df_test]:
        df["days_to_license_expiry"] = (
            pd.to_datetime(df["LICENSE TERM EXPIRATION DATE"])
            - pd.to_datetime(df["Inspection Date"])
        ).dt.days
        df["license_expiry_missing"] = df["days_to_license_expiry"].isna().astype(int)

    median_expiry = df_train["days_to_license_expiry"].median()
    logger.info("Median days to license expiry (train): {:.0f} days", median_expiry)

    df_train["days_to_license_expiry"] = df_train["days_to_license_expiry"].fillna(median_expiry)
    df_val["days_to_license_expiry"] = df_val["days_to_license_expiry"].fillna(median_expiry)
    df_test["days_to_license_expiry"] = df_test["days_to_license_expiry"].fillna(median_expiry)

    logger.info(
        "Remaining nulls — train: {}, val: {}, test: {}",
        df_train["days_to_license_expiry"].isna().sum(),
        df_val["days_to_license_expiry"].isna().sum(),
        df_test["days_to_license_expiry"].isna().sum(),
    )

    return df_train, df_val, df_test

def segment_inspection_date(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train = df_train.copy()
    df_val = df_val.copy()
    df_test = df_test.copy()

    for df in [df_train, df_val, df_test]:
        df["inspection_year"] = df["Inspection Date"].dt.year
        df["inspection_month"] = df["Inspection Date"].dt.month
        df["inspection_dayofweek"] = df["Inspection Date"].dt.dayofweek
        df["inspection_quarter"] = df["Inspection Date"].dt.quarter

    logger.info(
        "Inspection date features extracted — train range: {} → {}",
        df_train["Inspection Date"].min().date(),
        df_train["Inspection Date"].max().date(),
    )
    logger.info(
        "inspection_year stats (train): min={}, max={}, nunique={}",
        int(df_train["inspection_year"].min()),
        int(df_train["inspection_year"].max()),
        df_train["inspection_year"].nunique(),
    )

    return df_train, df_val, df_test


def apply_feature_engineering(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train, df_val, df_test = encode_risk(df_train, df_val, df_test)
    df_train, df_val, df_test = parse_dates(df_train, df_val, df_test)
    df_train, df_val, df_test = engineer_license_expiry(df_train, df_val, df_test)
    df_train, df_val, df_test = segment_inspection_date(df_train, df_val, df_test)
    return df_train, df_val, df_test
