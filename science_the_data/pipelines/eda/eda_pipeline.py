from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from loguru import logger

from science_the_data.eda import correlations, distributions, geo, missing, temporal
from science_the_data.helpers.path_resolver import PathResolver
from science_the_data.helpers.types import DataSplits, PipelineStage

EDA_CACHE_DIR = Path("eda_cache")
TARGET = "Results"


def _load(csv_name: str, stage: PipelineStage) -> pd.DataFrame:
    path = PathResolver.get_data_path_from_stage(csv_name, stage)
    logger.info("Loading {} ...", path)
    cols = pd.read_csv(path, nrows=0).columns.tolist()
    parse_dates = ["Inspection Date"] if "Inspection Date" in cols else []
    return pd.read_csv(path, parse_dates=parse_dates)


def eda_pipeline(splits: DataSplits) -> None:
    stage = PipelineStage.PROCESSED

    logger.info("=== EDA Pipeline ===")

    # Use train split for all EDA — val/test stay held-out
    df = _load(splits.train, stage)
    logger.info("Train set: {:,} rows × {} columns", len(df), df.shape[1])

    payload: dict = {}

    # --- Class balance ---
    logger.info("Computing class balance ...")
    payload["class_balance"] = distributions.class_balance(df, TARGET)
    logger.info(
        "Class balance — Pass: {:.1f}%  Fail: {:.1f}%",
        payload["class_balance"]["pct"].get(0, 0),
        payload["class_balance"]["pct"].get(1, 0),
    )

    # --- Numeric summary ---
    logger.info("Computing numeric summary ...")
    payload["numeric_summary"] = distributions.numeric_summary(df)

    # --- Categorical distributions ---
    logger.info("Computing categorical distributions ...")
    payload["top_facility_types"] = distributions.top_facility_types(df)
    payload["risk_distribution"] = distributions.risk_distribution(df)
    payload["inspection_type_distribution"] = distributions.inspection_type_distribution(df)

    # --- Missing values ---
    logger.info("Computing missing value summary ...")
    payload["missing_summary"] = missing.missing_summary(df)
    n_missing_cols = len(payload["missing_summary"])
    if n_missing_cols:
        logger.warning("{} column(s) have missing values", n_missing_cols)
    else:
        logger.info("No missing values found")

    # --- Correlations ---
    logger.info("Computing correlations ...")
    payload["numeric_correlation"] = correlations.numeric_correlation(df)
    payload["target_correlation"]  = correlations.target_correlation(df, TARGET)
    logger.info(
        "Top correlate with target: {} ({:.3f})",
        payload["target_correlation"].index[0] if not payload["target_correlation"].empty else "N/A",
        payload["target_correlation"].iloc[0]  if not payload["target_correlation"].empty else 0,
    )

    # --- Temporal ---
    logger.info("Computing temporal trends ...")
    payload["inspections_over_time"] = temporal.inspections_over_time(df)
    payload["fail_rate_over_time"]   = temporal.fail_rate_over_time(df)

    # --- Geo ---
    logger.info("Computing geo distributions ...")
    payload["geo_sample"]             = geo.geo_sample(df)
    payload["fail_rate_by_community"] = geo.fail_rate_by_community(df)

    # --- Persist for dashboard ---
    EDA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = EDA_CACHE_DIR / "eda_payload.pkl"
    with open(cache_path, "wb") as f:
        pickle.dump(payload, f)
    logger.success("EDA cache written → {}", cache_path)

    logger.info("=== EDA Pipeline complete ===")