from __future__ import annotations

from pathlib import Path
import pickle

from loguru import logger

from science_the_data.eda import correlations, distributions, missing
from science_the_data.helpers.splits_io import load_splits
from science_the_data.helpers.types import DataSplits, PipelineStage

EDA_CACHE_DIR = Path("eda_cache")
TARGET = "Results"


def eda_final_pipeline(splits: DataSplits) -> None:
    stage = PipelineStage.PROCESSED

    logger.info("=== EDA Pipeline ===")

    df_train, _, _ = load_splits(*splits.as_tuple(), stage)

    logger.info("Train set: {:,} rows × {} columns", len(df_train), df_train.shape[1])

    payload: dict = {}

    logger.info("Computing class balance ...")
    payload["class_balance"] = distributions.class_balance(df_train, TARGET)
    logger.info(
        "Class balance — Pass: {:.1f}%  Fail: {:.1f}%",
        payload["class_balance"]["pct"].get(0, 0),
        payload["class_balance"]["pct"].get(1, 0),
    )

    logger.info("Computing numeric summary ...")
    payload["numeric_summary"] = distributions.numeric_summary(df_train)

    logger.info("Computing categorical distributions ...")
    payload["top_facility_types"] = distributions.top_facility_types(df_train)
    payload["risk_distribution"] = distributions.risk_distribution(df_train)
    payload["inspection_type_distribution"] = distributions.inspection_type_distribution(df_train)

    logger.info("Computing missing value summary ...")
    payload["missing_summary"] = missing.missing_summary(df_train)
    n_missing_cols = len(payload["missing_summary"])
    if n_missing_cols:
        logger.warning("{} column(s) have missing values", n_missing_cols)
    else:
        logger.info("No missing values found")

    logger.info("Computing correlations ...")
    payload["numeric_correlation"] = correlations.numeric_correlation(df_train)
    payload["target_correlation"] = correlations.target_correlation(df_train, TARGET)
    logger.info(
        "Top correlate with target: {} ({:.3f})",
        payload["target_correlation"].index[0]
        if not payload["target_correlation"].empty
        else "N/A",
        payload["target_correlation"].iloc[0] if not payload["target_correlation"].empty else 0,
    )

    logger.info("Computing violation statistics...")
    payload["violations"] = distributions.violation_summary(df_train)

    if payload["violations"]:
        logger.info(
            "Average violations per inspection: {:.2f}", payload["violations"]["mean_violations"]
        )

    EDA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = EDA_CACHE_DIR / "eda_payload.pkl"

    with open(cache_path, "wb") as f:
        pickle.dump(payload, f)

    logger.success("EDA cache written → {}", cache_path)

    logger.info("=== EDA Pipeline complete ===")
