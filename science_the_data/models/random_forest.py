from __future__ import annotations

import joblib
from pathlib import Path

import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestClassifier

from models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[RandomForestClassifier, dict, dict]:

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    train_metrics = evaluate(model, X_train, y_train, "Random Forest — Train")
    val_metrics   = evaluate(model, X_val,   y_val,   "Random Forest — Val")

    importance_df = pd.DataFrame({
        "feature":    X_train.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    logger.info("Feature importances:\n{}", importance_df.to_string(index=False))

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "random_forest.pkl")
    logger.info("Model saved → {}", models_dir / "random_forest.pkl")

    return model, train_metrics, val_metrics