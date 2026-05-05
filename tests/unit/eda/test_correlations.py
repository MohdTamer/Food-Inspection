from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.eda.correlations import numeric_correlation, target_correlation


class TestNumericCorrelation:
    def test_returns_dataframe(self, base_df):
        assert isinstance(numeric_correlation(base_df), pd.DataFrame)

    def test_only_numeric_columns(self, base_df):
        result = numeric_correlation(base_df)
        assert set(result.columns).issubset({"Latitude", "Longitude", "score"})

    def test_symmetric(self, base_df):
        result = numeric_correlation(base_df)
        pd.testing.assert_frame_equal(result, result.T)

    def test_diagonal_is_one(self, base_df):
        result = numeric_correlation(base_df)
        for col in result.columns:
            assert result.loc[col, col] == pytest.approx(1.0)

    def test_empty_df_returns_empty(self):
        assert numeric_correlation(pd.DataFrame()).empty

    def test_no_numeric_columns_returns_empty(self):
        df = pd.DataFrame({"a": ["x", "y"], "b": ["p", "q"]})
        assert numeric_correlation(df).empty


class TestTargetCorrelation:
    def test_returns_series(self, numeric_results_df):
        assert isinstance(target_correlation(numeric_results_df, target="Results"), pd.Series)

    def test_target_not_in_result(self, numeric_results_df):
        result = target_correlation(numeric_results_df, target="Results")
        assert "Results" not in result.index

    def test_missing_target_returns_empty(self, base_df):
        assert target_correlation(base_df, target="NonExistentColumn").empty

    def test_sorted_by_abs_value(self, numeric_results_df):
        result = target_correlation(numeric_results_df, target="Results")
        abs_vals = result.abs().tolist()
        assert abs_vals == sorted(abs_vals, reverse=True)