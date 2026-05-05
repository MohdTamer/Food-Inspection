from __future__ import annotations

import pandas as pd

from science_the_data.eda.temporal import inspections_over_time, fail_rate_over_time


class TestInspectionsOverTime:
    def test_returns_series(self, base_df):
        assert isinstance(inspections_over_time(base_df), pd.Series)

    def test_missing_date_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Inspection Date"])
        assert inspections_over_time(df).empty

    def test_counts_are_positive(self, base_df):
        assert (inspections_over_time(base_df) >= 0).all()

    def test_total_equals_non_null_dates(self, base_df):
        result = inspections_over_time(base_df)
        non_null = pd.to_datetime(base_df["Inspection Date"], errors="coerce").notna().sum()
        assert result.sum() == non_null

    def test_monthly_has_more_buckets_than_quarterly(self, base_df):
        monthly = inspections_over_time(base_df, freq="ME")
        quarterly = inspections_over_time(base_df, freq="QE")
        assert len(monthly) >= len(quarterly)


class TestFailRateOverTime:
    def test_returns_series(self, numeric_results_df):
        assert isinstance(fail_rate_over_time(numeric_results_df), pd.Series)

    def test_missing_date_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Inspection Date"])
        assert fail_rate_over_time(df).empty

    def test_missing_results_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["Results"])
        assert fail_rate_over_time(df).empty

    def test_values_between_0_and_1(self, numeric_results_df):
        result = fail_rate_over_time(numeric_results_df)
        assert (result >= 0).all() and (result <= 1).all()