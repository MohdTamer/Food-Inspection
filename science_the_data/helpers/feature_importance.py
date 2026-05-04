from __future__ import annotations

import pandas as pd


def get_feature_importance(model, feature_names: list[str]) -> pd.DataFrame | None:
    """Extract a feature-importance DataFrame from any supported model or Pipeline.

    Returns a DataFrame with columns ['feature', 'importance'] sorted descending,
    or None for models that have no importance concept (e.g. KNN).

    Supported:
      - sklearn / XGBoost estimators with .feature_importances_  (DT, RF, XGBoost)
      - LogisticRegression via |coef_[0]|
      - Any sklearn or imblearn Pipeline wrapping the above
    """
    estimator = _unwrap(model)

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        # For multi-class coef_ is 2-D; binary is (1, n_features)
        coef = estimator.coef_
        importances = abs(coef[0] if coef.ndim == 2 else coef)
    else:
        return None

    return (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def _unwrap(model):
    """Unwrap the final estimator from a sklearn or imblearn Pipeline."""
    if hasattr(model, "named_steps"):
        return list(model.named_steps.values())[-1]
    return model
