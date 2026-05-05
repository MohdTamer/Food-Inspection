from __future__ import annotations

import mlflow


def log_metrics_to_mlflow(metrics: dict, prefix: str) -> None:
    """Log the standard evaluation metrics dict to the active MLflow run.

    Call once per split (e.g. prefix='val', prefix='test').
    Designed to accept the dict returned by models.evaluation.evaluate().
    """
    mlflow.log_metric(f"{prefix}_accuracy", metrics["accuracy"])
    mlflow.log_metric(f"{prefix}_balanced_accuracy", metrics["balanced_accuracy"])
    mlflow.log_metric(f"{prefix}_f1_weighted", metrics["f1_weighted"])
    mlflow.log_metric(f"{prefix}_f1_fail", metrics["f1_fail"])
    mlflow.log_metric(f"{prefix}_f1_pass", metrics["f1_pass"])
    mlflow.log_metric(f"{prefix}_mcc", metrics["mcc"])
    mlflow.log_metric(f"{prefix}_pr_auc", metrics["pr_auc"])
    mlflow.log_metric(f"{prefix}_brier_score", metrics["brier_score"])
    mlflow.log_metric(f"{prefix}_precision_fail", metrics["precision_fail"])
    mlflow.log_metric(f"{prefix}_recall_fail", metrics["recall_fail"])
    mlflow.log_metric(f"{prefix}_false_negative_rate", metrics["false_negative_rate"])
    mlflow.log_metric(f"{prefix}_false_positive_rate", metrics["false_positive_rate"])
    mlflow.log_metric(f"{prefix}_sensitivity", metrics["sensitivity"])
    mlflow.log_metric(f"{prefix}_roc_auc", metrics["roc_auc"])
