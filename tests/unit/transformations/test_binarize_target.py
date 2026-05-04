from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.transformations.binarize_target import (
    PwC_THRESHOLD,
    TARGET_MAP,
    binarize_target,
    count_violations,
)


class TestCountViolations:

    def test_counts_pipe_separated_violations(self):
        series = pd.Series(["v1 | v2 | v3"])
        result = count_violations(series)
        assert result.iloc[0] == 3

    def test_single_violation_returns_one(self):
        series = pd.Series(["v1"])
        result = count_violations(series)
        assert result.iloc[0] == 1

    def test_empty_string_returns_zero(self):
        series = pd.Series([""])
        result = count_violations(series)
        assert result.iloc[0] == 0

    def test_whitespace_only_returns_zero(self):
        series = pd.Series(["   "])
        result = count_violations(series)
        assert result.iloc[0] == 0

    def test_null_returns_zero(self):
        series = pd.Series([None])
        result = count_violations(series)
        assert result.iloc[0] == 0

    def test_multiple_rows(self):
        series = pd.Series(["v1 | v2", "", "v1 | v2 | v3 | v4"])
        result = count_violations(series)
        assert result.iloc[0] == 2
        assert result.iloc[1] == 0
        assert result.iloc[2] == 4


class TestBinarizeTarget:


    def test_pass_mapped_to_zero(self):
        df = pd.DataFrame({"Results": ["Pass"], "Violations": [""]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 0

    def test_fail_mapped_to_one(self):
        df = pd.DataFrame({"Results": ["Fail"], "Violations": ["v1 | v2"]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 1


    def test_pwc_below_threshold_mapped_to_zero(self):
        violations = " | ".join([f"v{i}" for i in range(PwC_THRESHOLD - 1)])
        df = pd.DataFrame({"Results": ["Pass w/ Conditions"], "Violations": [violations]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 0

    def test_pwc_at_threshold_mapped_to_one(self):
        violations = " | ".join([f"v{i}" for i in range(PwC_THRESHOLD)])
        df = pd.DataFrame({"Results": ["Pass w/ Conditions"], "Violations": [violations]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 1

    def test_pwc_above_threshold_mapped_to_one(self):
        violations = " | ".join([f"v{i}" for i in range(PwC_THRESHOLD + 2)])
        df = pd.DataFrame({"Results": ["Pass w/ Conditions"], "Violations": [violations]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 1

    def test_pwc_with_no_violations_mapped_to_zero(self):
        df = pd.DataFrame({"Results": ["Pass w/ Conditions"], "Violations": [""]})
        result = binarize_target(df)
        assert result["Results"].iloc[0] == 0


    def test_results_column_is_int(self):
        df = pd.DataFrame({"Results": ["Pass", "Fail"], "Violations": ["", "v1"]})
        result = binarize_target(df)
        assert result["Results"].dtype == int

    def test_violation_count_column_dropped(self):
        df = pd.DataFrame({"Results": ["Pass"], "Violations": [""]})
        result = binarize_target(df)
        assert "violation_count" not in result.columns

    def test_no_nulls_in_results_after_binarization(self):
        df = pd.DataFrame({
            "Results":    ["Pass", "Fail", "Pass w/ Conditions"],
            "Violations": ["", "v1", "v1 | v2"],
        })
        result = binarize_target(df)
        assert result["Results"].isna().sum() == 0

    def test_other_columns_preserved(self):
        df = pd.DataFrame({
            "Results":    ["Pass"],
            "Violations": [""],
            "Risk":       [1],
        })
        result = binarize_target(df)
        assert "Risk" in result.columns


    def test_raises_on_unmapped_result_value(self):
        df = pd.DataFrame({"Results": ["Unknown Value"], "Violations": [""]})
        with pytest.raises(AssertionError, match="Unmapped values"):
            binarize_target(df)


    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame({"Results": ["Pass"], "Violations": [""]})
        original_value = df["Results"].iloc[0]
        binarize_target(df)
        assert df["Results"].iloc[0] == original_value