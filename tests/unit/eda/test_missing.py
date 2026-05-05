from __future__ import annotations

import pandas as pd

from science_the_data.eda.missing import missing_summary


class TestMissingSummary:
    def test_returns_dataframe(self, base_df):
        assert isinstance(missing_summary(base_df), pd.DataFrame)

    def test_only_columns_with_nulls(self, base_df):
        result = missing_summary(base_df)
        for col in result.index:
            assert base_df[col].isnull().sum() > 0

    def test_columns_present(self, base_df):
        result = missing_summary(base_df)
        assert "missing_count" in result.columns
        assert "missing_pct" in result.columns

    def test_sorted_descending(self, base_df):
        result = missing_summary(base_df)
        pcts = result["missing_pct"].tolist()
        assert pcts == sorted(pcts, reverse=True)

    def test_no_nulls_returns_empty(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        assert missing_summary(df).empty