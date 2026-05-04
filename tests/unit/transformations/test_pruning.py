from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.transformations.pruning import (
    FLAG_COLS,
    NOISE_COLS,
    PRUNE_COLS,
    RAW_DATE_COLS,
    prune_columns,
)


class TestPruneColumns:


    def test_drops_noise_columns(self):
        df = pd.DataFrame(columns=NOISE_COLS + ["Results"])
        result, dropped = prune_columns(df)
        for col in NOISE_COLS:
            assert col not in result.columns

    def test_drops_flag_columns(self):
        df = pd.DataFrame(columns=FLAG_COLS + ["Results"])
        result, dropped = prune_columns(df)
        for col in FLAG_COLS:
            assert col not in result.columns

    def test_drops_raw_date_columns(self):
        df = pd.DataFrame(columns=RAW_DATE_COLS + ["Results"])
        result, dropped = prune_columns(df)
        for col in RAW_DATE_COLS:
            assert col not in result.columns

    def test_drops_all_prune_cols_at_once(self):
        df = pd.DataFrame(columns=PRUNE_COLS + ["Results", "Risk"])
        result, dropped = prune_columns(df)
        for col in PRUNE_COLS:
            assert col not in result.columns


    def test_keeps_columns_not_in_prune_list(self):
        df = pd.DataFrame(columns=PRUNE_COLS + ["Results", "Risk", "Inspection Date"])
        result, _ = prune_columns(df)
        assert "Results" in result.columns
        assert "Risk" in result.columns
        assert "Inspection Date" in result.columns


    def test_returns_list_of_dropped_columns(self):
        df = pd.DataFrame(columns=PRUNE_COLS + ["Results"])
        _, dropped = prune_columns(df)
        assert isinstance(dropped, list)
        assert set(dropped) == set(PRUNE_COLS)

    def test_dropped_list_excludes_missing_columns(self):
        df = pd.DataFrame(columns=["Results", "DBA Name"])
        _, dropped = prune_columns(df)
        assert "DBA Name" in dropped
        # columns not in df should not appear in dropped
        for col in PRUNE_COLS:
            if col != "DBA Name":
                assert col not in dropped

    def test_dropped_list_empty_when_no_prune_cols_present(self):
        df = pd.DataFrame(columns=["Results", "Risk"])
        _, dropped = prune_columns(df)
        assert dropped == []


    def test_does_not_raise_when_prune_col_missing(self):
        df = pd.DataFrame(columns=["Results"])
        result, dropped = prune_columns(df)
        assert "Results" in result.columns
        assert dropped == []

    def test_works_when_all_prune_cols_missing(self):
        df = pd.DataFrame({"Results": [0, 1], "Risk": [1, 2]})
        result, dropped = prune_columns(df)
        assert list(result.columns) == ["Results", "Risk"]
        assert dropped == []


    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame(columns=PRUNE_COLS)
        result, dropped = prune_columns(df)
        assert result.empty
        assert set(dropped) == set(PRUNE_COLS)

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame(columns=PRUNE_COLS + ["Results"])
        original_cols = list(df.columns)
        prune_columns(df)
        assert list(df.columns) == original_cols

    def test_row_count_unchanged_after_pruning(self):
        df = pd.DataFrame({col: [1, 2, 3] for col in PRUNE_COLS + ["Results"]})
        result, _ = prune_columns(df)
        assert len(result) == 3