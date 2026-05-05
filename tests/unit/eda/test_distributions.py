from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.eda.distributions import (
    class_balance,
    cardinality_summary,
    numeric_summary,
    top_facility_types,
    risk_distribution,
    inspection_type_distribution,
    violation_summary,
)


class TestClassBalance:
    def test_counts_sum_to_total(self, base_df):
        result = class_balance(base_df)
        assert sum(result["counts"].values()) == len(base_df)

    def test_pcts_sum_to_100(self, base_df):
        result = class_balance(base_df)
        assert sum(result["pct"].values()) == pytest.approx(100.0, rel=1e-3)

    def test_keys_present(self, base_df):
        result = class_balance(base_df)
        assert "counts" in result and "pct" in result

    def test_custom_target(self, base_df):
        result = class_balance(base_df, target="Risk")
        assert "Risk 1 (High)" in result["counts"]


class TestCardinalitySummary:
    def test_returns_dataframe_with_expected_columns(self, base_df):
        result = cardinality_summary(base_df)
        assert "unique_values" in result.columns
        assert "dtype" in result.columns

    def test_sorted_descending(self, base_df):
        result = cardinality_summary(base_df)
        vals = result["unique_values"].tolist()
        assert vals == sorted(vals, reverse=True)

    def test_all_columns_present(self, base_df):
        result = cardinality_summary(base_df)
        assert set(result.index) == set(base_df.columns)


class TestNumericSummary:
    def test_returns_dataframe(self, base_df):
        assert isinstance(numeric_summary(base_df), pd.DataFrame)

    def test_has_skew_column(self, base_df):
        assert "skew" in numeric_summary(base_df).columns

    def test_standard_describe_rows_present(self, base_df):
        result = numeric_summary(base_df)
        for stat in ["mean", "std", "min", "max"]:
            assert stat in result.columns

    def test_only_numeric_columns(self, base_df):
        result = numeric_summary(base_df)
        numeric_cols = base_df.select_dtypes(include="number").columns.tolist()
        assert set(result.index).issubset(set(numeric_cols))


class TestTopFacilityTypes:
    def test_returns_series(self, base_df):
        assert isinstance(top_facility_types(base_df), pd.Series)

    def test_respects_n(self, base_df):
        assert len(top_facility_types(base_df, n=2)) <= 2

    def test_missing_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Facility Type"])
        assert top_facility_types(df).empty

    def test_fallback_to_encoded_column(self, base_df):
        df = base_df.drop(columns=["Facility Type"])
        df["facility_type_encoded"] = [0, 1, 0, 2, 0]
        assert not top_facility_types(df).empty


class TestRiskDistribution:
    def test_returns_series(self, base_df):
        assert isinstance(risk_distribution(base_df), pd.Series)

    def test_sorted_by_index(self, base_df):
        result = risk_distribution(base_df)
        assert result.index.tolist() == sorted(result.index.tolist())

    def test_missing_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Risk"])
        assert risk_distribution(df).empty


class TestInspectionTypeDistribution:
    def test_returns_series(self, base_df):
        assert isinstance(inspection_type_distribution(base_df), pd.Series)

    def test_missing_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Inspection Type"])
        assert inspection_type_distribution(df).empty

    def test_fallback_to_encoded_column(self, base_df):
        df = base_df.drop(columns=["Inspection Type"])
        df["inspection_type_encoded"] = [0, 1, 2, 0, 1]
        assert not inspection_type_distribution(df).empty


class TestViolationSummary:
    def test_returns_dict_with_expected_keys(self, base_df):
        result = violation_summary(base_df)
        for key in ["mean_violations", "max_violations", "distribution"]:
            assert key in result

    def test_missing_violations_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Violations"])
        assert violation_summary(df) == {}

    def test_mean_is_positive(self, base_df):
        assert violation_summary(base_df)["mean_violations"] >= 0

    def test_uses_precomputed_violation_count(self, base_df):
        df = base_df.drop(columns=["Violations"])
        df["violation_count"] = [1, 2, 3, 0, 4]
        df["Results"] = [0, 1, 0, 0, 1]
        assert violation_summary(df)["max_violations"] == 4