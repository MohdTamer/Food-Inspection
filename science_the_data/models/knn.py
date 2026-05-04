from __future__ import annotations

from pathlib import Path

import joblib
from loguru import logger
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[Pipeline, dict, dict]:

    # KNN is sensitive to scale — wrap in pipeline
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "model",
                KNeighborsClassifier(
                    n_neighbors=11,
                    weights="distance",
                    metric="euclidean",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)

    train_metrics = evaluate(pipeline, X_train, y_train, "KNN — Train")
    val_metrics = evaluate(pipeline, X_val, y_val, "KNN — Val")

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "knn.pkl")
    logger.info("Model saved → {}", models_dir / "knn.pkl")

    return pipeline, train_metrics, val_metrics
