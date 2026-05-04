from __future__ import annotations

import pandas as pd
from loguru import logger
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


def evaluate(model, X: pd.DataFrame, y: pd.Series, split_name: str) -> dict:
    y_pred  = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]
    cm      = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "split":   split_name,
        "roc_auc": round(roc_auc_score(y, y_proba), 4),
        "fnr":     round(fn / (fn + tp), 4),
        "fpr":     round(fp / (fp + tn), 4),
    }

    logger.info(
        "{} — ROC-AUC: {}  FNR: {}  FPR: {}",
        split_name, metrics["roc_auc"], metrics["fnr"], metrics["fpr"],
    )
    logger.info("\n{}", classification_report(y, y_pred, target_names=["Pass", "Fail"]))

    return metrics