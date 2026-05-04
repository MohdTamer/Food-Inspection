from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.cleaning.quarintine import quarantine_missing_results


class TestQuarantineMissingResults:

    def test_clean_rows_are_returned_in_clean_df(self):
        df = pd.DataFrame({"Results": ["Pass", "Fail"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(clean) == 2
        assert len(quarantined) == 0

    def test_quarantines_null_results(self):
        df = pd.DataFrame({"Results": [None, "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(clean) == 1
        assert len(quarantined) == 1

    def test_quarantines_empty_string_results(self):
        df = pd.DataFrame({"Results": ["", "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(clean) == 1
        assert len(quarantined) == 1

    def test_quarantines_not_ready(self):
        df = pd.DataFrame({"Results": ["Not Ready", "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(quarantined) == 1
        assert len(clean) == 1

    def test_quarantines_business_not_located(self):
        df = pd.DataFrame({"Results": ["Business Not Located", "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(quarantined) == 1

    def test_quarantines_out_of_business(self):
        df = pd.DataFrame({"Results": ["Out of Business", "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(quarantined) == 1

    def test_quarantines_no_entry(self):
        df = pd.DataFrame({"Results": ["No Entry", "Pass"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(quarantined) == 1

    def test_quarantines_all_invalid_values_together(self):
        df = pd.DataFrame({
            "Results": ["Not Ready", "Business Not Located", "Out of Business", "No Entry", None, "", "Pass"]
        })
        clean, quarantined = quarantine_missing_results(df)
        assert len(quarantined) == 6
        assert len(clean) == 1

    def test_quarantined_rows_have_quarantine_reason_column(self):
        df = pd.DataFrame({"Results": [None, "Pass"]})
        _, quarantined = quarantine_missing_results(df)
        assert "quarantine_reason" in quarantined.columns

    def test_quarantine_reason_value_is_missing_results(self):
        df = pd.DataFrame({"Results": [None]})
        _, quarantined = quarantine_missing_results(df)
        assert quarantined["quarantine_reason"].iloc[0] == "missing_results"

    def test_clean_df_does_not_have_quarantine_reason_column(self):
        df = pd.DataFrame({"Results": ["Pass", "Fail"]})
        clean, _ = quarantine_missing_results(df)
        assert "quarantine_reason" not in clean.columns

    def test_returns_full_df_when_no_results_column(self):
        df = pd.DataFrame({"some_col": [1, 2, 3]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(clean) == 3
        assert len(quarantined) == 0

    def test_quarantined_has_correct_columns_when_no_results_column(self):
        df = pd.DataFrame({"some_col": [1, 2]})
        clean, quarantined = quarantine_missing_results(df)
        assert list(quarantined.columns) == list(df.columns)

    def test_clean_results_are_stripped(self):
        df = pd.DataFrame({"Results": ["  Pass  ", "Fail"]})
        clean, _ = quarantine_missing_results(df)
        assert clean["Results"].iloc[0] == "Pass"

    def test_other_columns_preserved_in_clean(self):
        df = pd.DataFrame({"Results": ["Pass", None], "Risk": [1, 2]})
        clean, _ = quarantine_missing_results(df)
        assert "Risk" in clean.columns
        assert clean["Risk"].iloc[0] == 1

    def test_other_columns_preserved_in_quarantined(self):
        df = pd.DataFrame({"Results": [None], "Risk": [3]})
        _, quarantined = quarantine_missing_results(df)
        assert "Risk" in quarantined.columns
        assert quarantined["Risk"].iloc[0] == 3

    def test_empty_dataframe_returns_two_empty_dfs(self):
        df = pd.DataFrame({"Results": []})
        clean, quarantined = quarantine_missing_results(df)
        assert clean.empty
        assert quarantined.empty

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame({"Results": [None, "Pass"]})
        original_len = len(df)
        quarantine_missing_results(df)
        assert len(df) == original_len
        assert "quarantine_reason" not in df.columns

    def test_clean_and_quarantined_rows_sum_to_original(self):
        df = pd.DataFrame({"Results": ["Pass", "Fail", None, "Not Ready", "Out of Business"]})
        clean, quarantined = quarantine_missing_results(df)
        assert len(clean) + len(quarantined) == len(df)