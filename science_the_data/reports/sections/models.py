from __future__ import annotations


def render_models(results: list[dict]) -> list[str]:
    """
    Render a Markdown section summarising model training results.

    Each result dict is expected to contain the fields produced by
    train_models_pipeline (val metrics at top level, test_* prefixed metrics).
    """
    lines: list[str] = []
    lines.append("## Model Training Results\n")

    if not results:
        lines.append("_No models were trained._\n")
        return lines

    # --- Summary table: val vs test ---
    lines.append("### Summary (Val → Test)\n")
    lines.append(
        "| Model | Val ROC-AUC | Test ROC-AUC | Val F1-Fail | Test F1-Fail | Val FNR | Test FNR |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for r in sorted(
        results, key=lambda x: x.get("test_roc_auc", x.get("roc_auc", 0)), reverse=True
    ):
        name = r.get("model", r.get("split", "Unknown"))
        lines.append(
            f"| {name}"
            f" | {r.get('roc_auc', 0):.4f}"
            f" | {r.get('test_roc_auc', 0):.4f}"
            f" | {r.get('f1_fail', 0):.4f}"
            f" | {r.get('test_f1_fail', 0):.4f}"
            f" | {r.get('fnr', r.get('false_negative_rate', 0)):.4f}"
            f" | {r.get('test_fnr', 0):.4f} |"
        )
    lines.append("")

    best = max(results, key=lambda x: x.get("test_roc_auc", x.get("roc_auc", 0)))
    best_name = best.get("model", best.get("split", "Unknown"))
    lines.append(
        f"> **Best model by Test ROC-AUC:** {best_name} "
        f"(`{best.get('test_roc_auc', best.get('roc_auc', 0)):.4f}`)\n"
    )

    # --- Per-model detail ---
    lines.append("### Per-Model Detail\n")
    for r in results:
        name = r.get("model", r.get("split", "Unknown"))
        lines.append(f"#### {name}\n")

        # Val metrics
        lines.append(f"- **Val ROC-AUC:** {r.get('roc_auc', 0):.4f}")
        lines.append(
            f"- **Val FNR:** {r.get('fnr', r.get('false_negative_rate', 0)):.4f}"
            f"  |  **Val FPR:** {r.get('fpr', r.get('false_positive_rate', 0)):.4f}"
        )
        if "accuracy" in r:
            lines.append(f"- **Val Accuracy:** {r['accuracy']:.4f}")
        lines.append("")

        # Test metrics
        if "test_roc_auc" in r:
            lines.append(f"- **Test ROC-AUC:** {r['test_roc_auc']:.4f}")
            lines.append(
                f"- **Test FNR:** {r.get('test_fnr', 0):.4f}"
                f"  |  **Test FPR:** {r.get('test_fpr', 0):.4f}"
            )
            lines.append(
                f"- **Test F1-Fail:** {r.get('test_f1_fail', 0):.4f}"
                f"  |  **Test Balanced Acc:** {r.get('test_balanced_accuracy', 0):.4f}"
            )
            lines.append("")

        # Train vs Val overfitting check
        if "train_roc_auc" in r:
            gap = r["train_roc_auc"] - r.get("roc_auc", 0)
            lines.append(f"- **Train ROC-AUC:** {r['train_roc_auc']:.4f}  (val gap: `{gap:+.4f}`)")
            lines.append("")

        # Val classification table
        has_clf = all(
            k in r
            for k in (
                "precision_pass",
                "recall_pass",
                "f1_pass",
                "precision_fail",
                "recall_fail",
                "f1_fail",
            )
        )
        if has_clf:
            lines.append("**Val classification report:**\n")
            lines.append("| Class | Precision | Recall | F1 |")
            lines.append("|---|---|---|---|")
            lines.append(
                f"| Pass | {r['precision_pass']:.4f} | {r['recall_pass']:.4f} | {r['f1_pass']:.4f} |"
            )
            lines.append(
                f"| Fail | {r['precision_fail']:.4f} | {r['recall_fail']:.4f} | {r['f1_fail']:.4f} |"
            )
            lines.append("")

        # Feature importances (top-10)
        if "feature_importances" in r and r["feature_importances"]:
            lines.append("**Top feature importances:**\n")
            lines.append("| Feature | Importance |")
            lines.append("|---|---|")
            for fi in r["feature_importances"][:10]:
                lines.append(f"| {fi['feature']} | {fi['importance']:.6f} |")
            lines.append("")

        # Best params (tuned models)
        if "best_params" in r and r["best_params"]:
            lines.append("**Best hyper-parameters:**")
            for k, v in r["best_params"].items():
                lines.append(f"- `{k}`: {v}")
            lines.append("")

    return lines
