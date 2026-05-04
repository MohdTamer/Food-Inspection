from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier

from science_the_data.models.evaluation import evaluate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def perfect_model_data():
    """Linearly-separable data so a shallow tree achieves perfect accuracy."""
    rng = np.random.default_rng(0)
    X = pd.DataFrame({"a": rng.uniform(0, 1, 200), "b": rng.uniform(0, 1, 200)})
    y = pd.Series((X["a"] > 0.5).astype(int), name="Results")
    model = DecisionTreeClassifier(max_depth=1, random_state=0).fit(X, y)
    return model, X, y


@pytest.fixture
def imbalanced_model_data():
    """70/30 split to mirror the real dataset's class distribution."""
    rng = np.random.default_rng(1)
    n = 300
    X = pd.DataFrame({"a": rng.uniform(0, 1, n), "b": rng.uniform(0, 1, n)})
    y = pd.Series((X["a"] > 0.3).astype(int), name="Results")  # ~70% fail
    model = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
    return model, X, y


# ---------------------------------------------------------------------------
# Return structure
# ---------------------------------------------------------------------------

class TestEvaluateReturnStructure:

    def test_returns_three_tuple(self, perfect_model_data):
        model, X, y = perfect_model_data
        result = evaluate(model, X, y, "Test")
        assert len(result) == 3

    def test_first_element_is_proba_array(self, perfect_model_data):
        model, X, y = perfect_model_data
        y_proba, _, _ = evaluate(model, X, y, "Test")
        assert isinstance(y_proba, np.ndarray)
        assert y_proba.shape == (len(y),)

    def test_second_element_is_confusion_matrix(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, cm, _ = evaluate(model, X, y, "Test")
        assert cm.shape == (2, 2)

    def test_third_element_is_dict(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, metrics = evaluate(model, X, y, "Test")
        assert isinstance(metrics, dict)


# ---------------------------------------------------------------------------
# Required keys
# ---------------------------------------------------------------------------

_REQUIRED_KEYS = [
    "split",
    "tp", "tn", "fp", "fn",
    "sensitivity", "specificity",
    "false_negative_rate", "false_positive_rate",
    "accuracy", "balanced_accuracy",
    "roc_auc", "pr_auc", "brier_score", "mcc",
    "precision_fail", "recall_fail", "f1_fail",
    "precision_pass", "recall_pass", "f1_pass",
    "f1_weighted",
    "fnr", "fpr",
]


class TestEvaluateKeys:

    def test_all_required_keys_present(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, metrics = evaluate(model, X, y, "Test")
        missing = [k for k in _REQUIRED_KEYS if k not in metrics]
        assert missing == [], f"Missing keys: {missing}"

    def test_split_name_stored(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, metrics = evaluate(model, X, y, "My Split")
        assert metrics["split"] == "My Split"


# ---------------------------------------------------------------------------
# Aliases consistency
# ---------------------------------------------------------------------------

class TestEvaluateAliases:

    def test_fnr_equals_false_negative_rate(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["fnr"] == m["false_negative_rate"]

    def test_fpr_equals_false_positive_rate(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["fpr"] == m["false_positive_rate"]

    def test_sensitivity_equals_recall_fail(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert abs(m["sensitivity"] - m["recall_fail"]) < 1e-9

    def test_specificity_equals_recall_pass(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert abs(m["specificity"] - m["recall_pass"]) < 1e-9


# ---------------------------------------------------------------------------
# Mathematical invariants
# ---------------------------------------------------------------------------

class TestEvaluateInvariants:

    def test_confusion_matrix_sums_to_n(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, cm, m = evaluate(model, X, y, "Test")
        assert m["tp"] + m["tn"] + m["fp"] + m["fn"] == len(y)

    def test_cm_ravel_matches_metrics_counts(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, cm, m = evaluate(model, X, y, "Test")
        tn, fp, fn, tp = cm.ravel()
        assert m["tp"] == tp
        assert m["tn"] == tn
        assert m["fp"] == fp
        assert m["fn"] == fn

    def test_fnr_plus_sensitivity_equals_one(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert abs(m["false_negative_rate"] + m["sensitivity"] - 1.0) < 1e-9

    def test_fpr_plus_specificity_equals_one(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert abs(m["false_positive_rate"] + m["specificity"] - 1.0) < 1e-9

    def test_probabilities_between_zero_and_one(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        y_proba, _, _ = evaluate(model, X, y, "Test")
        assert (y_proba >= 0).all() and (y_proba <= 1).all()

    def test_metrics_in_valid_range(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        for key in ("roc_auc", "accuracy", "balanced_accuracy", "f1_fail", "f1_pass"):
            assert 0.0 <= m[key] <= 1.0, f"{key}={m[key]} out of [0, 1]"

    def test_mcc_in_valid_range(self, imbalanced_model_data):
        model, X, y = imbalanced_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert -1.0 <= m["mcc"] <= 1.0


# ---------------------------------------------------------------------------
# Edge cases — perfect and all-wrong predictions
# ---------------------------------------------------------------------------

class TestEvaluatePerfectModel:

    def test_perfect_model_fnr_is_zero(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["false_negative_rate"] == pytest.approx(0.0)

    def test_perfect_model_fpr_is_zero(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["false_positive_rate"] == pytest.approx(0.0)

    def test_perfect_model_roc_auc_is_one(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["roc_auc"] == pytest.approx(1.0)

    def test_perfect_model_no_false_negatives(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["fn"] == 0

    def test_perfect_model_no_false_positives(self, perfect_model_data):
        model, X, y = perfect_model_data
        _, _, m = evaluate(model, X, y, "Test")
        assert m["fp"] == 0
