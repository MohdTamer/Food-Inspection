from __future__ import annotations

from pathlib import Path

import joblib
from loguru import logger
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from science_the_data.models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[Pipeline, dict, dict]:

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)

    _, _, train_metrics = evaluate(pipeline, X_train, y_train, "Logistic Regression — Train")
    _, _, val_metrics = evaluate(pipeline, X_val, y_val, "Logistic Regression — Val")

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "logistic_regression.pkl")
    logger.info("Model saved → {}", models_dir / "logistic_regression.pkl")

    return pipeline, train_metrics, val_metrics
