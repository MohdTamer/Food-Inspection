from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.transformations.inspection_history_encoding import (
    add_inspection_history_features,
)


def _make_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["Inspection Date"] = pd.to_datetime(df["Inspection Date"])
    return df


def _base_row(license: int, date: str, results: int) -> dict:
    return {"License #": license, "Inspection Date": date, "Results": results}


class TestAddInspectionHistoryFeatures:


    def test_days_since_last_inspection_column_added(self):
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(1, "2021-01-01", 0)])
        test  = _make_df([_base_row(1, "2021-06-01", 1)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert "days_since_last_inspection" in t.columns

    def test_prev_inspection_result_column_added(self):
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(1, "2021-01-01", 0)])
        test  = _make_df([_base_row(1, "2021-06-01", 1)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert "prev_inspection_result" in t.columns

    def test_fail_rate_last_3_column_added(self):
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(1, "2021-01-01", 0)])
        test  = _make_df([_base_row(1, "2021-06-01", 1)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert "fail_rate_last_3" in t.columns


    def test_days_since_last_inspection_correct_value(self):
        train = _make_df([
            _base_row(1, "2020-01-01", 0),
            _base_row(1, "2020-04-10", 1),  # 100 days later
        ])
        val  = _make_df([_base_row(2, "2020-01-01", 0)])
        test = _make_df([_base_row(2, "2020-06-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        second = t.sort_values("Inspection Date").iloc[1]
        assert second["days_since_last_inspection"] == 100

    def test_first_inspection_has_no_null_days(self):
        # train needs 2 inspections for the same license so the median gap is not NaN
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 0)])
        val   = _make_df([_base_row(2, "2021-01-01", 0)])
        test  = _make_df([_base_row(3, "2022-01-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert t["days_since_last_inspection"].isna().sum() == 0


    def test_prev_inspection_result_correct_value(self):
        train = _make_df([
            _base_row(1, "2020-01-01", 1),
            _base_row(1, "2020-06-01", 0),
        ])
        val  = _make_df([_base_row(2, "2020-01-01", 0)])
        test = _make_df([_base_row(2, "2020-06-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        sorted_t = t.sort_values("Inspection Date")
        assert sorted_t["prev_inspection_result"].iloc[1] == 1.0

    def test_first_inspection_prev_result_filled(self):
        # train needs 2 inspections so prev_mean is not NaN
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(2, "2021-01-01", 0)])
        test  = _make_df([_base_row(3, "2022-01-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert t["prev_inspection_result"].isna().sum() == 0


    def test_fail_rate_last_3_excludes_current_row(self):
        # 3 inspections: fail, fail, pass — fail_rate for 3rd should be based on first 2
        train = _make_df([
            _base_row(1, "2020-01-01", 1),
            _base_row(1, "2020-06-01", 1),
            _base_row(1, "2021-01-01", 0),
        ])
        val  = _make_df([_base_row(2, "2020-01-01", 0)])
        test = _make_df([_base_row(2, "2020-06-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        sorted_t = t.sort_values("Inspection Date")
        assert abs(sorted_t["fail_rate_last_3"].iloc[2] - 1.0) < 1e-6

    def test_fail_rate_last_3_no_nulls(self):
        # train needs 2 inspections so fail_mean is not NaN
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(2, "2021-01-01", 0)])
        test  = _make_df([_base_row(3, "2022-01-01", 0)])
        t, _, _ = add_inspection_history_features(train, val, test)
        assert t["fail_rate_last_3"].isna().sum() == 0


    def test_null_fill_uses_train_statistics_not_val(self):
        # train has 2 inspections for same license — both failures → prev_mean = 1.0
        # val has only passes → if val stats were used, fill would be 0.0
        train = _make_df([_base_row(1, "2020-01-01", 1), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(2, "2021-01-01", 0)])
        test  = _make_df([_base_row(3, "2022-01-01", 0)])
        t, v, e = add_inspection_history_features(train, val, test)
        # val first inspection has no prior — should be filled with train mean (1.0)
        assert abs(v["prev_inspection_result"].iloc[0] - 1.0) < 1e-6


    def test_split_column_not_present_in_output(self):
        train = _make_df([_base_row(1, "2020-01-01", 0)])
        val   = _make_df([_base_row(2, "2020-06-01", 0)])
        test  = _make_df([_base_row(3, "2021-01-01", 0)])
        t, v, e = add_inspection_history_features(train, val, test)
        assert "_split" not in t.columns
        assert "_split" not in v.columns
        assert "_split" not in e.columns

    def test_row_counts_preserved_per_split(self):
        train = _make_df([_base_row(1, "2020-01-01", 0), _base_row(1, "2020-06-01", 1)])
        val   = _make_df([_base_row(2, "2021-01-01", 0)])
        test  = _make_df([_base_row(3, "2022-01-01", 1)])
        t, v, e = add_inspection_history_features(train, val, test)
        assert len(t) == 2
        assert len(v) == 1
        assert len(e) == 1

    def test_does_not_mutate_original_dataframes(self):
        train = _make_df([_base_row(1, "2020-01-01", 0)])
        val   = _make_df([_base_row(2, "2020-06-01", 0)])
        test  = _make_df([_base_row(3, "2021-01-01", 0)])
        original_cols = list(train.columns)
        add_inspection_history_features(train, val, test)
        assert list(train.columns) == original_cols