from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.cleaning.drop_useless_columns import (
    COLS_TO_DROP,
    drop_useless_columns,
)

class TestDropUselessColumns:

    def test_drops_all_defined_useless_columns(self):
        df = pd.DataFrame(columns=COLS_TO_DROP + ["Results", "Risk"])
        result = drop_useless_columns(df)
        for col in COLS_TO_DROP:
            assert col not in result.columns

    def test_keeps_columns_not_in_drop_list(self):
        df = pd.DataFrame(columns=COLS_TO_DROP + ["Results", "Risk", "Inspection Date"])
        result = drop_useless_columns(df)
        assert "Results" in result.columns
        assert "Risk" in result.columns
        assert "Inspection Date" in result.columns

    def test_drops_known_columns(self):
        """Spot check a few key columns from each category in COLS_TO_DROP"""
        cols = [
           "BL_ADDRESS",
            "BL_CITY",
            "BL_STATE",
            "BL_ZIP_CODE",
            "BL_LATITUDE",
            "BL_LONGITUDE",
            "BL_LOCATION",
            "BL_LEGAL_NAME",
            "BL_DBA_NAME",
            # Fully null columns from the dataset for some reason
            "Historical Wards 2003-2015",
            "Zip Codes",
            "Community Areas",
            "Census Tracts",
            "Wards",
            # Administrative IDs with no predictive value
            "BL_ID",
            "BL_LICENSE_ID",
            "ACCOUNT NUMBER",
            "SITE NUMBER",
            # Political/administrative boundaries
            "WARD",
            "PRECINCT",
            "WARD PRECINCT",
            "POLICE DISTRICT",
            "SSA",
            # Licensing process snapshots (not establishment state)
            "APPLICATION CREATED DATE",
            "APPLICATION REQUIREMENTS COMPLETE",
            "PAYMENT DATE",
            "CONDITIONAL APPROVAL",
            "LICENSE APPROVED FOR ISSUANCE",
            "DATE ISSUED",
            "LICENSE STATUS CHANGE DATE",
            # Business activity — not used downstream
            "BUSINESS ACTIVITY ID",
            "BUSINESS ACTIVITY",
            # Join keys — already served their purpose
            "LICENSE NUMBER",
            "LICENSE CODE",
            # Redundant with COMMUNITY AREA NAME
            "NEIGHBORHOOD",
            "COMMUNITY AREA",
        ]
        df = pd.DataFrame(columns=cols + ["Results"])
        result = drop_useless_columns(df)
        for col in cols:
            assert col not in result.columns
        assert "Results" in result.columns

    def test_accepts_custom_cols_to_drop(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
        result = drop_useless_columns(df, cols_to_drop=["a", "b"])
        assert "a" not in result.columns
        assert "b" not in result.columns
        assert "c" in result.columns

    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame(columns=COLS_TO_DROP)
        result = drop_useless_columns(df)
        assert result.empty

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame(columns=COLS_TO_DROP + ["Results"])
        original_cols = list(df.columns)
        drop_useless_columns(df)
        assert list(df.columns) == original_cols

    def test_dataframe_with_no_useless_columns_unchanged(self):
        df = pd.DataFrame({"Results": [0, 1], "Risk": [1, 2]})
        result = drop_useless_columns(df, cols_to_drop=[])
        assert list(result.columns) == ["Results", "Risk"]