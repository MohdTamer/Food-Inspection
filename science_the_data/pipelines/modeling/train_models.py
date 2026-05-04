from __future__ import annotations

from pathlib import Path

from loguru import logger
import pandas as pd

from helpers.splits_io import load_splits
from helpers.types import PipelineStage
from science_the_data.helpers.feature_importance import get_feature_importance
from science_the_data.models import (
    decision_tree,
    knn,
    logistic_regression,
    random_forest,
    xgboost,
)
from science_the_data.models.evaluation import evaluate

MODELS_DIR = Path("models")
TARGET = "Results"

_STEPS = [
    ("Logistic Regression", logistic_regression),
    ("KNN", knn),
    ("Decision Tree", decision_tree),
    ("Random Forest", random_forest),
    ("XGBoost", xgboost),
]


def _format_comparison_table(summary: pd.DataFrame) -> str:
    header = (
        f"{'Model':<22} "
        f"{'ROC-AUC':>10}  "
        f"{'F1-Fail':>10}  "
        f"{'FNR':>10}  "
        f"{'Bal-Acc':>10}  "
        f"{'PR-AUC':>10}"
    )
    sub = (
        f"{'':<22} "
        f"{'Val':>5} {'Test':>5}  "
        f"{'Val':>5} {'Test':>5}  "
        f"{'Val':>5} {'Test':>5}  "
        f"{'Val':>5} {'Test':>5}  "
        f"{'Val':>5} {'Test':>5}"
    )
    sep = "-" * len(header)
    lines = ["=== Model Comparison (Val vs Test) ===", sep, header, sub, sep]
    for _, r in summary.iterrows():
        lines.append(
            f"{r['model']:<22} "
            f"{r.get('roc_auc', 0):>5.3f} {r.get('test_roc_auc', 0):>5.3f}  "
            f"{r.get('f1_fail', 0):>5.3f} {r.get('test_f1_fail', 0):>5.3f}  "
            f"{r.get('fnr', 0):>5.3f} {r.get('test_fnr', 0):>5.3f}  "
            f"{r.get('balanced_accuracy', 0):>5.3f} {r.get('test_balanced_accuracy', 0):>5.3f}  "
            f"{r.get('pr_auc', 0):>5.3f} {r.get('test_pr_auc', 0):>5.3f}"
        )
    lines.append(sep)
    return "\n".join(lines)


def train_models_pipeline(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
) -> list[dict]:
    """Train all models, evaluate on val + test, return per-model result dicts."""

    train, val, test = load_splits(train_csv_name, val_csv_name, test_csv_name, input_stage)

    for df in [train, val, test]:
        bool_cols = df.select_dtypes(include="bool").columns
        df[bool_cols] = df[bool_cols].astype(int)

    X_train, y_train = train.drop(columns=TARGET), train[TARGET]
    X_val, y_val = val.drop(columns=TARGET), val[TARGET]
    X_test, y_test = test.drop(columns=TARGET), test[TARGET]

    feature_names = X_train.columns.tolist()
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for name, module in _STEPS:
        logger.info("Training {}...", name)
        model, train_m, val_m = module.train(X_train, y_train, X_val, y_val, MODELS_DIR)
        _, _, test_m = evaluate(model, X_test, y_test, f"{name} — Test")

        results.append(
            {
                "model": name,
                # flat val metrics at top level (keeps render_models / reporting working)
                **val_m,
                # train metrics for overfitting check
                "train_roc_auc": train_m["roc_auc"],
                "train_fnr": train_m["false_negative_rate"],
                "train_fpr": train_m["false_positive_rate"],
                "train_f1_fail": train_m["f1_fail"],
                "train_balanced_accuracy": train_m["balanced_accuracy"],
                # test metrics (honest final evaluation)
                "test_roc_auc": test_m["roc_auc"],
                "test_f1_fail": test_m["f1_fail"],
                "test_fnr": test_m["false_negative_rate"],
                "test_fpr": test_m["false_positive_rate"],
                "test_balanced_accuracy": test_m["balanced_accuracy"],
                "test_pr_auc": test_m["pr_auc"],
                "test_mcc": test_m["mcc"],
                "test_precision_fail": test_m["precision_fail"],
                "test_recall_fail": test_m["recall_fail"],
            }
        )

        imp_df = get_feature_importance(model, feature_names)
        if imp_df is not None:
            imp_df.insert(0, "model", name)
            slug = name.lower().replace(" ", "_")
            imp_path = logs_dir / f"feature_importance_{slug}.csv"
            imp_df.to_csv(imp_path, index=False)
            logger.info(
                "{} — top features:\n{}",
                name,
                imp_df.head(5).to_string(index=False),
            )
        else:
            logger.info("{} — no feature importances available", name)

    summary = pd.DataFrame(results).sort_values("test_roc_auc", ascending=False)
    logger.info("\n{}", _format_comparison_table(summary))

    summary_path = logs_dir / "model_comparison.csv"
    summary.to_csv(summary_path, index=False)
    logger.info("Saved model comparison → {}", summary_path)

    return results
