from __future__ import annotations

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate(
    model, X: pd.DataFrame, y: pd.Series, split_name: str
) -> tuple[np.ndarray, np.ndarray, dict]:
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]
    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel()

    fnr = fn / (fn + tp)
    fpr = fp / (fp + tn)
    tpr = tp / (tp + fn)
    tnr = tn / (tn + fp)

    roc_auc = roc_auc_score(y, y_proba)
    pr_auc = average_precision_score(y, y_proba)
    brier = brier_score_loss(y, y_proba)
    mcc = matthews_corrcoef(y, y_pred)
    bal_acc = balanced_accuracy_score(y, y_pred)
    f1_fail = f1_score(y, y_pred, pos_label=1, zero_division=0)
    f1_pass = f1_score(y, y_pred, pos_label=0, zero_division=0)
    f1_weighted = f1_score(y, y_pred, average="weighted", zero_division=0)
    prec_fail = precision_score(y, y_pred, pos_label=1, zero_division=0)
    recall_fail = recall_score(y, y_pred, pos_label=1, zero_division=0)
    prec_pass = precision_score(y, y_pred, pos_label=0, zero_division=0)
    recall_pass = recall_score(y, y_pred, pos_label=0, zero_division=0)

    logger.info(
        "{} — ROC-AUC: {:.4f}  PR-AUC: {:.4f}  F1-Fail: {:.4f}  FNR: {:.4f}",
        split_name,
        roc_auc,
        pr_auc,
        f1_fail,
        fnr,
    )
    logger.info("\n{}", classification_report(y, y_pred, target_names=["Pass", "Fail"]))

    metrics = {
        "split": split_name,
        # counts
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        # rates
        "sensitivity": tpr,
        "specificity": tnr,
        "false_negative_rate": fnr,
        "false_positive_rate": fpr,
        # model quality
        "accuracy": accuracy_score(y, y_pred),
        "balanced_accuracy": bal_acc,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier_score": brier,
        "mcc": mcc,
        # per class — Fail
        "precision_fail": prec_fail,
        "recall_fail": recall_fail,
        "f1_fail": f1_fail,
        # per class — Pass
        "precision_pass": prec_pass,
        "recall_pass": recall_pass,
        "f1_pass": f1_pass,
        "f1_weighted": f1_weighted,
        # backward-compat aliases used by reports
        "fnr": fnr,
        "fpr": fpr,
    }

    return y_proba, cm, metrics
