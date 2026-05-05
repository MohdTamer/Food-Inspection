from __future__ import annotations

from pathlib import Path

import joblib
from loguru import logger
import numpy as np
import pandas as pd
from scipy.stats import randint
from sklearn.model_selection import PredefinedSplit, RandomizedSearchCV
from sklearn.tree import DecisionTreeClassifier

from science_the_data.models.evaluation import evaluate


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    models_dir: Path,
) -> tuple[DecisionTreeClassifier, dict, dict]:

    X_search = pd.concat([X_train, X_val], ignore_index=True)
    y_search = pd.concat([y_train, y_val], ignore_index=True)
    split_index = np.concatenate(
        [
            np.full(len(X_train), -1),
            np.full(len(X_val), 0),
        ]
    )
    ps = PredefinedSplit(split_index)

    param_dist = {
        "max_depth": randint(3, 20),
        "min_samples_split": randint(2, 50),
        "min_samples_leaf": randint(1, 30),
        "criterion": ["gini", "entropy"],
        "max_features": [None, "sqrt", "log2"],
        "class_weight": ["balanced", None],
    }

    search = RandomizedSearchCV(
        DecisionTreeClassifier(random_state=42),
        param_distributions=param_dist,
        n_iter=80,
        scoring="f1_weighted",
        cv=ps,
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_search, y_search)

    best_params = search.best_params_
    logger.info("Best params: {}", best_params)

    model = DecisionTreeClassifier(**best_params, random_state=42)
    model.fit(X_train, y_train)

    logger.info("Tree depth: {}  Leaf nodes: {}", model.get_depth(), model.get_n_leaves())

    _, _, train_metrics = evaluate(model, X_train, y_train, "Decision Tree — Train")
    _, _, val_metrics = evaluate(model, X_val, y_val, "Decision Tree — Val")

    importance_df = pd.DataFrame(
        {
            "feature": X_train.columns,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    logger.info("Feature importances:\n{}", importance_df.to_string(index=False))

    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models_dir / "decision_tree.pkl")
    logger.info("Model saved → {}", models_dir / "decision_tree.pkl")

    return model, train_metrics, val_metrics
