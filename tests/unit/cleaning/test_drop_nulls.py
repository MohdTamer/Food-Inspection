# tests/unit/test_drop_nulls.py

import pandas as pd
import pytest
from science_the_data.cleaning.drop_nulls import (
    drop_fully_nulls_columns,
    drop_exact_duplicates,
    drop_inspection_id_duplication,
)

def test_drop_nulls_removes_fully_null_column():
    df = pd.DataFrame({"a": [1, 2], "b": [None, None]})
    result = drop_fully_nulls_columns(df)
    assert "b" not in result.columns

def test_drop_nulls_keeps_partially_null_column():
    df = pd.DataFrame({"a": [1, None], "b": [None, None]})
    result = drop_fully_nulls_columns(df)
    assert "a" in result.columns

def test_drop_nulls_keeps_all_columns_when_none_fully_null():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = drop_fully_nulls_columns(df)
    assert list(result.columns) == ["a", "b"]

def test_drop_nulls_drops_multiple_fully_null_columns():
    df = pd.DataFrame({"a": [1, 2], "b": [None, None], "c": [None, None]})
    result = drop_fully_nulls_columns(df)
    assert "b" not in result.columns
    assert "c" not in result.columns
    assert "a" in result.columns

def test_drop_nulls_row_count_unchanged():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [None, None, None]})
    result = drop_fully_nulls_columns(df)
    assert len(result) == 3

def test_exact_duplicates_removes_duplicate_row():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    result = drop_exact_duplicates(df)
    assert len(result) == 2

def test_exact_duplicates_keeps_first_occurrence():
    df = pd.DataFrame({"a": [1, 1], "b": ["keep", "keep"]})
    result = drop_exact_duplicates(df)
    assert len(result) == 1
    assert result.iloc[0]["a"] == 1

def test_exact_duplicates_no_duplicates_unchanged():
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = drop_exact_duplicates(df)
    assert len(result) == 3

def test_exact_duplicates_partial_match_is_not_duplicate():
    df = pd.DataFrame({
        "Inspection ID": [1, 1],
        "Results":       ["Pass", "Fail"],
    })
    result = drop_exact_duplicates(df)
    assert len(result) == 2

def test_exact_duplicates_all_identical_rows_leaves_one():
    df = pd.DataFrame({"a": [5, 5, 5]})
    result = drop_exact_duplicates(df)
    assert len(result) == 1

def test_inspection_id_keeps_latest_date():
    df = pd.DataFrame({
        "Inspection ID":   [1, 1],
        "Inspection Date": ["2023-01-01", "2023-06-01"],
        "Results":         ["Fail", "Pass"],
    })
    result = drop_inspection_id_duplication(df)
    assert len(result) == 1
    assert result.iloc[0]["Results"] == "Pass"  # the 2023-06-01 row

def test_inspection_id_preserves_unique_ids():
    df = pd.DataFrame({
        "Inspection ID":   [1, 2, 3],
        "Inspection Date": ["2023-01-01", "2022-05-10", "2021-03-15"],
        "Results":         ["Pass", "Fail", "Pass"],
    })
    result = drop_inspection_id_duplication(df)
    assert len(result) == 3

def test_inspection_id_output_ids_are_unique():
    df = pd.DataFrame({
        "Inspection ID":   [1, 1, 2, 2, 3],
        "Inspection Date": ["2022-01-01", "2023-01-01",
                            "2021-05-01", "2023-05-01", "2020-01-01"],
        "Results":         ["Fail", "Pass", "Pass", "Fail", "Pass"],
    })
    result = drop_inspection_id_duplication(df)
    assert result["Inspection ID"].nunique() == len(result)

def test_inspection_id_works_without_date_column():
    df = pd.DataFrame({
        "Inspection ID": [1, 1, 2],
        "Results":       ["Pass", "Pass", "Fail"],
    })
    result = drop_inspection_id_duplication(df)
    assert result["Inspection ID"].nunique() == len(result)

def test_inspection_id_no_leftover_sort_column():
    df = pd.DataFrame({
        "Inspection ID":   [1, 1],
        "Inspection Date": ["2022-01-01", "2023-01-01"],
    })
    result = drop_inspection_id_duplication(df)
    assert "_sort_inspection_date" not in result.columns

def test_inspection_id_handles_unparseable_dates():
    df = pd.DataFrame({
        "Inspection ID":   [1, 1],
        "Inspection Date": ["not-a-date", "also-bad"],
    })
    result = drop_inspection_id_duplication(df)
    assert len(result) == 1