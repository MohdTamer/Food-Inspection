from __future__ import annotations


def render_models(results: list[dict]) -> list[str]:
    """
    Render a Markdown section summarising model training results.

    Parameters
    ----------
    results : list of per-model dicts, each containing:
        - split      : e.g. "XGBoost — Val"
        - roc_auc    : float
        - fnr        : float
        - fpr        : float
        - (optional) precision_pass, recall_pass, f1_pass
        - (optional) precision_fail, recall_fail, f1_fail
        - (optional) accuracy
        - (optional) train_roc_auc, train_fnr, train_fpr  (for overfitting check)
        - (optional) feature_importances : list[dict] with keys "feature", "importance"
        - (optional) best_params : dict
    """
    lines: list[str] = []

    lines.append("## Model Training Results\n")

    if not results:
        lines.append("_No models were trained._\n")
        return lines

    # --- Validation summary table ---
    lines.append("### Validation Summary\n")
    lines.append("| Model | ROC-AUC | FNR | FPR |")
    lines.append("|---|---|---|---|")
    for r in sorted(results, key=lambda x: x.get("roc_auc", 0), reverse=True):
        name = r.get("split", "Unknown")
        lines.append(
            f"| {name} | {r.get('roc_auc', 0):.4f} | {r.get('fnr', 0):.4f} | {r.get('fpr', 0):.4f} |"
        )
    lines.append("")

    best = max(results, key=lambda x: x.get("roc_auc", 0))
    lines.append(
        f"> **Best model by ROC-AUC:** {best.get('split', 'Unknown')} "
        f"(`{best.get('roc_auc', 0):.4f}`)\n"
    )

    # --- Per-model detail ---
    lines.append("### Per-Model Detail\n")
    for r in results:
        name = r.get("split", "Unknown")
        lines.append(f"#### {name}\n")

        # Core metrics
        lines.append(f"- **ROC-AUC:** {r.get('roc_auc', 0):.4f}")
        lines.append(f"- **FNR:** {r.get('fnr', 0):.4f}  |  **FPR:** {r.get('fpr', 0):.4f}")
        if "accuracy" in r:
            lines.append(f"- **Accuracy:** {r['accuracy']:.4f}")
        lines.append("")

        # Train vs Val overfitting check
        if "train_roc_auc" in r:
            gap = r["train_roc_auc"] - r.get("roc_auc", 0)
            lines.append(f"- **Train ROC-AUC:** {r['train_roc_auc']:.4f}  (gap: `{gap:+.4f}`)")
            lines.append("")

        # Classification report table
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
            lines.append("| Class | Precision | Recall | F1 |")
            lines.append("|---|---|---|---|")
            lines.append(
                f"| Pass | {r['precision_pass']:.2f} | {r['recall_pass']:.2f} | {r['f1_pass']:.2f} |"
            )
            lines.append(
                f"| Fail | {r['precision_fail']:.2f} | {r['recall_fail']:.2f} | {r['f1_fail']:.2f} |"
            )
            lines.append("")

        # Best params (Decision Tree / tuned models)
        if "best_params" in r and r["best_params"]:
            lines.append("**Best hyper-parameters:**")
            for k, v in r["best_params"].items():
                lines.append(f"- `{k}`: {v}")
            lines.append("")

        # Feature importances (top-10)
        if "feature_importances" in r and r["feature_importances"]:
            lines.append("**Top feature importances:**\n")
            lines.append("| Feature | Importance |")
            lines.append("|---|---|")
            for fi in r["feature_importances"][:10]:
                lines.append(f"| {fi['feature']} | {fi['importance']:.6f} |")
            lines.append("")

    return lines
