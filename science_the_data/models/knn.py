from __future__ import annotations

from pathlib import Path

import joblib
from loguru import logger
import pandas as pd
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from science_the_data.models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[Pipeline, dict, dict]:

    # RandomUnderSampler balances the training set before KNN fits.
    # During predict/predict_proba the sampler is skipped — only the scaler applies.
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("sampler", RandomUnderSampler(random_state=42)),
            (
                "model",
                KNeighborsClassifier(
                    n_neighbors=21,
                    weights="distance",
                    metric="euclidean",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)

    _, _, train_metrics = evaluate(pipeline, X_train, y_train, "KNN — Train")
    _, _, val_metrics = evaluate(pipeline, X_val, y_val, "KNN — Val")

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, models_dir / "knn.pkl")
    logger.info("Model saved → {}", models_dir / "knn.pkl")

    return pipeline, train_metrics, val_metrics
