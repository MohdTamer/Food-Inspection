from __future__ import annotations

from pathlib import Path

from loguru import logger
import pandas as pd

from helpers.splits_io import load_splits
from helpers.types import PipelineStage
from science_the_data.models import (
    decision_tree,
    knn,
    logistic_regression,
    random_forest,
    xgboost,
)

MODELS_DIR = Path("models")
TARGET = "Results"

_STEPS = [
    ("Logistic Regression", logistic_regression),
    ("KNN", knn),
    ("Decision Tree", decision_tree),
    ("Random Forest", random_forest),
    ("XGBoost", xgboost),
]


def train_models_pipeline(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
) -> list[dict]:
    """Train all models and return a list of per-model result dicts for reporting."""

    train, val, _ = load_splits(train_csv_name, val_csv_name, test_csv_name, input_stage)

    for df in [train, val]:
        bool_cols = df.select_dtypes(include="bool").columns
        df[bool_cols] = df[bool_cols].astype(int)

    X_train, y_train = train.drop(columns=TARGET), train[TARGET]
    X_val, y_val = val.drop(columns=TARGET), val[TARGET]

    results: list[dict] = []

    for name, module in _STEPS:
        logger.info("Training {}...", name)
        _, train_m, val_m = module.train(X_train, y_train, X_val, y_val, MODELS_DIR)
        results.append(
            {
                **val_m,
                "train_roc_auc": train_m["roc_auc"],
                "train_fnr": train_m["fnr"],
                "train_fpr": train_m["fpr"],
            }
        )

    summary = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
    logger.info("\n=== Validation Summary ===\n{}", summary.to_string(index=False))

    summary_path = Path("logs/model_comparison.csv")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)
    logger.info("Saved model comparison → {}", summary_path)

    return results
