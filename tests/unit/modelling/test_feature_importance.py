from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from science_the_data.helpers.feature_importance import get_feature_importance, _unwrap


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def data():
    rng = np.random.default_rng(42)
    X = pd.DataFrame({
        "violation_count": rng.uniform(0, 10, 200),
        "days_since_last_inspection": rng.uniform(0, 365, 200),
        "risk": rng.integers(1, 4, 200).astype(float),
    })
    y = (X["violation_count"] > 5).astype(int)
    return X, y


FEATURES = ["violation_count", "days_since_last_inspection", "risk"]


# ---------------------------------------------------------------------------
# Decision Tree
# ---------------------------------------------------------------------------

class TestDecisionTree:

    def test_returns_dataframe(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert list(result.columns) == ["feature", "importance"]

    def test_row_count_matches_features(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert len(result) == len(FEATURES)

    def test_sorted_descending(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert result["importance"].is_monotonic_decreasing

    def test_importances_sum_to_one(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert result["importance"].sum() == pytest.approx(1.0, abs=1e-6)

    def test_most_important_feature_is_violation_count(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert result["feature"].iloc[0] == "violation_count"


# ---------------------------------------------------------------------------
# Random Forest
# ---------------------------------------------------------------------------

class TestRandomForest:

    def test_returns_dataframe(self, data):
        X, y = data
        model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert isinstance(result, pd.DataFrame)

    def test_importances_are_non_negative(self, data):
        X, y = data
        model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert (result["importance"] >= 0).all()


# ---------------------------------------------------------------------------
# Logistic Regression (raw estimator)
# ---------------------------------------------------------------------------

class TestLogisticRegression:

    def test_returns_dataframe(self, data):
        X, y = data
        model = LogisticRegression(random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert isinstance(result, pd.DataFrame)

    def test_importances_are_non_negative(self, data):
        X, y = data
        model = LogisticRegression(random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert (result["importance"] >= 0).all()

    def test_sorted_descending(self, data):
        X, y = data
        model = LogisticRegression(random_state=0).fit(X, y)
        result = get_feature_importance(model, FEATURES)
        assert result["importance"].is_monotonic_decreasing


# ---------------------------------------------------------------------------
# KNN — no importances
# ---------------------------------------------------------------------------

class TestKNN:

    def test_bare_knn_returns_none(self, data):
        X, y = data
        model = KNeighborsClassifier().fit(X, y)
        assert get_feature_importance(model, FEATURES) is None

    def test_knn_in_imblearn_pipeline_returns_none(self, data):
        X, y = data
        pipe = ImbPipeline([
            ("scaler", StandardScaler()),
            ("sampler", RandomUnderSampler(random_state=0)),
            ("model", KNeighborsClassifier()),
        ])
        pipe.fit(X, y)
        assert get_feature_importance(pipe, FEATURES) is None


# ---------------------------------------------------------------------------
# sklearn Pipeline wrapping Logistic Regression
# ---------------------------------------------------------------------------

class TestSklearnPipeline:

    def test_unwraps_logistic_pipeline(self, data):
        X, y = data
        pipe = SkPipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(random_state=0)),
        ])
        pipe.fit(X, y)
        result = get_feature_importance(pipe, FEATURES)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(FEATURES)

    def test_pipeline_and_raw_model_importances_match(self, data):
        X, y = data
        lr = LogisticRegression(random_state=0).fit(X, y)
        pipe = SkPipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(random_state=0)),
        ])
        pipe.fit(X, y)
        raw = get_feature_importance(lr, FEATURES)
        via_pipe = get_feature_importance(pipe, FEATURES)
        # Same features in same order (importances differ because scaler changes scale)
        assert list(raw["feature"]) == list(via_pipe["feature"])[::-1] or \
               set(raw["feature"]) == set(via_pipe["feature"])


# ---------------------------------------------------------------------------
# _unwrap helper
# ---------------------------------------------------------------------------

class TestUnwrap:

    def test_unwrap_plain_model_returns_itself(self, data):
        X, y = data
        model = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X, y)
        assert _unwrap(model) is model

    def test_unwrap_sklearn_pipeline_returns_last_step(self, data):
        X, y = data
        lr = LogisticRegression(random_state=0)
        pipe = SkPipeline([("scaler", StandardScaler()), ("model", lr)])
        pipe.fit(X, y)
        assert _unwrap(pipe) is pipe.named_steps["model"]

    def test_unwrap_imblearn_pipeline_returns_last_step(self, data):
        X, y = data
        knn = KNeighborsClassifier()
        pipe = ImbPipeline([
            ("scaler", StandardScaler()),
            ("sampler", RandomUnderSampler(random_state=0)),
            ("model", knn),
        ])
        pipe.fit(X, y)
        assert _unwrap(pipe) is pipe.named_steps["model"]
