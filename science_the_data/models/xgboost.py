from __future__ import annotations

import joblib
from pathlib import Path

import pandas as pd
from loguru import logger
from xgboost import XGBClassifier

from models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[XGBClassifier, dict, dict]:

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    model = XGBClassifier(
        scale_pos_weight=scale_pos_weight,
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
        eval_metric="auc",
        early_stopping_rounds=20,
        verbosity=0,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    logger.info("XGBoost best iteration: {}", model.best_iteration)

    train_metrics = evaluate(model, X_train, y_train, "XGBoost — Train")
    val_metrics   = evaluate(model, X_val,   y_val,   "XGBoost — Val")

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "xgboost.pkl")
    logger.info("Model saved → {}", models_dir / "xgboost.pkl")

    return model, train_metrics, val_metrics