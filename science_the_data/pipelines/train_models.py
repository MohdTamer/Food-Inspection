from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger

from helpers.splits_io import load_splits
from helpers.types import PipelineStage
from models import decision_tree, knn, logistic_regression, random_forest, xgboost

MODELS_DIR = Path("models")
TARGET     = "Results"


def train_models_pipeline(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
) -> None:

    train, val, test = load_splits(train_csv_name, val_csv_name, test_csv_name, input_stage)

    # bool columns to int for sklearn compatibility
    for df in [train, val, test]:
        bool_cols = df.select_dtypes(include="bool").columns
        df[bool_cols] = df[bool_cols].astype(int)

    X_train, y_train = train.drop(columns=TARGET), train[TARGET]
    X_val,   y_val   = val.drop(columns=TARGET),   val[TARGET]

    results = []

    logger.info("Training Logistic Regression...")
    _, _, m = logistic_regression.train(X_train, y_train, X_val, y_val, MODELS_DIR)
    results.append(m)

    logger.info("Training KNN...")
    _, _, m = knn.train(X_train, y_train, X_val, y_val, MODELS_DIR)
    results.append(m)

    logger.info("Training Decision Tree...")
    _, _, m = decision_tree.train(X_train, y_train, X_val, y_val, MODELS_DIR)
    results.append(m)

    logger.info("Training Random Forest...")
    _, _, m = random_forest.train(X_train, y_train, X_val, y_val, MODELS_DIR)
    results.append(m)

    logger.info("Training XGBoost...")
    _, _, m = xgboost.train(X_train, y_train, X_val, y_val, MODELS_DIR)
    results.append(m)

    summary = pd.DataFrame(results).sort_values("roc_auc", ascending=False)
    logger.info("\n=== Validation Summary ===\n{}", summary.to_string(index=False))

    summary_path = Path("logs/model_comparison.csv")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)
    logger.info("Saved model comparison → {}", summary_path)