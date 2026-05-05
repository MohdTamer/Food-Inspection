from __future__ import annotations

from pathlib import Path
import pickle

from loguru import logger
import pandas as pd

from science_the_data.helpers.path_resolver import PathResolver
from science_the_data.transformations.binarize_target import count_violations

EDA_CACHE_DIR = Path("eda_cache")


def eda_raw_pipeline(raw_csv_name: str) -> None:
    raw_csv_path = PathResolver.get_raw_data_path(raw_csv_name)

    df = pd.read_csv(raw_csv_path)
    logger.info("Raw dataset: {:,} rows × {} cols", len(df), df.shape[1])

    payload: dict = {"stage": "raw"}

    logger.info("Computing business tenure ...")
    for col in ["DATE ISSUED", "APPLICATION CREATED DATE", "Inspection Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "DATE ISSUED" in df.columns and "Inspection Date" in df.columns:
        df["business_tenure_days"] = (df["Inspection Date"] - df["DATE ISSUED"]).dt.days
        if "APPLICATION CREATED DATE" in df.columns:
            mask = df["business_tenure_days"].isna()
            df.loc[mask, "business_tenure_days"] = (
                df.loc[mask, "Inspection Date"] - df.loc[mask, "APPLICATION CREATED DATE"]
            ).dt.days
        df.loc[df["business_tenure_days"] < 0, "business_tenure_days"] = None

        df["violation_count"] = (
            count_violations(df["Violations"]) if "Violations" in df.columns else 0
        )

        results_map = {"Pass": 0, "Fail": 1}
        df["_result_bin"] = df["Results"].map(results_map)
        pwc_mask = df["Results"] == "Pass w/ Conditions"
        df.loc[pwc_mask, "_result_bin"] = (df.loc[pwc_mask, "violation_count"] >= 4).astype(int)

        tenure_stats: dict = {
            "describe": df["business_tenure_days"].describe().to_dict(),
            "missing": int(df["business_tenure_days"].isna().sum()),
            "negative_count": int((df["business_tenure_days"] < 0).sum()),
        }

        bins = list(range(0, 5001, 365))
        labels = [f"{b // 365}y" for b in bins[:-1]]
        df["tenure_bin"] = pd.cut(df["business_tenure_days"], bins=bins, labels=labels)

        tenure_by_class: dict = {}
        for cls in [0, 1]:
            subset = df[df["_result_bin"] == cls]["tenure_bin"].value_counts().sort_index()
            tenure_by_class[cls] = subset.to_dict()

        tenure_stats["by_class"] = tenure_by_class
        payload["business_tenure"] = tenure_stats
        logger.info(
            "Business tenure — missing: {}, mean: {:.0f} days",
            tenure_stats["missing"],
            tenure_stats["describe"].get("mean", 0),
        )

    if "Violations" in df.columns:
        logger.info("Computing raw violation counts ...")
        df["violation_count"] = count_violations(df["Violations"])
        payload["raw_violations"] = {
            "describe": df["violation_count"].describe().to_dict(),
            "distribution": df["violation_count"].value_counts().sort_index().head(30).to_dict(),
        }

    EDA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = EDA_CACHE_DIR / "eda_raw_payload.pkl"
    with open(cache_path, "wb") as f:
        pickle.dump(payload, f)

    logger.success("Raw EDA cache written → {}", cache_path)
    logger.info("=== EDA Raw Pipeline complete ===")
