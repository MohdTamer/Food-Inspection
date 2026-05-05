from __future__ import annotations

import pandas as pd

from science_the_data.eda.geo import geo_sample, fail_rate_by_community


class TestGeoSample:
    def test_returns_dataframe(self, base_df):
        assert isinstance(geo_sample(base_df), pd.DataFrame)

    def test_respects_n(self, base_df):
        assert len(geo_sample(base_df, n=2)) <= 2

    def test_missing_lat_lon_returns_empty(self, base_df):
        df = base_df.drop(columns=["Latitude", "Longitude"])
        assert geo_sample(df).empty

    def test_drops_null_coords(self, base_df):
        # base_df row 3 has Latitude=None
        result = geo_sample(base_df)
        assert result["Latitude"].notna().all()
        assert result["Longitude"].notna().all()

    def test_deterministic_with_seed(self, base_df):
        r1 = geo_sample(base_df, seed=0)
        r2 = geo_sample(base_df, seed=0)
        pd.testing.assert_frame_equal(r1, r2)


class TestFailRateByCommunity:
    def test_returns_dataframe(self, numeric_results_df):
        assert isinstance(fail_rate_by_community(numeric_results_df), pd.DataFrame)

    def test_has_expected_columns(self, numeric_results_df):
        result = fail_rate_by_community(numeric_results_df)
        assert "COMMUNITY AREA NAME" in result.columns
        assert "fail_rate" in result.columns

    def test_missing_column_returns_empty(self, base_df):
        df = base_df.drop(columns=["COMMUNITY AREA NAME"])
        assert fail_rate_by_community(df).empty

    def test_sorted_descending(self, numeric_results_df):
        result = fail_rate_by_community(numeric_results_df)
        rates = result["fail_rate"].tolist()
        assert rates == sorted(rates, reverse=True)