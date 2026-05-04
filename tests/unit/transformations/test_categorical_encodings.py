from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.transformations.categorical_encodings import (
    APP_TYPE_MAP,
    NO_LONGER_NEEDED,
    encode_categorical_features,
)


def _make_splits(
    train_rows: list[dict],
    val_rows: list[dict] | None = None,
    test_rows: list[dict] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Helper to build minimal train/val/test DataFrames."""
    train = pd.DataFrame(train_rows)
    val   = pd.DataFrame(val_rows   or train_rows)
    test  = pd.DataFrame(test_rows  or train_rows)
    return train, val, test


def _base_row(
    inspection_type: str = "Canvass",
    facility_type: str   = "Restaurant",
    results: int         = 0,
    license_status: str  = "AAC",
    application_type: str = "RENEW",
) -> dict:
    return {
        "Inspection Type":  inspection_type,
        "Facility Type":    facility_type,
        "Results":          results,
        "LICENSE STATUS":   license_status,
        "APPLICATION TYPE": application_type,
    }


class TestEncodeCategoricalFeatures:


    def test_inspection_type_encoded_column_added(self):
        train, val, test = _make_splits([_base_row()])
        t, v, e = encode_categorical_features(train, val, test)
        assert "inspection_type_encoded" in t.columns
        assert "inspection_type_encoded" in v.columns
        assert "inspection_type_encoded" in e.columns

    def test_inspection_type_encoded_reflects_train_fail_rate(self):
        rows = [_base_row(results=1), _base_row(results=1), _base_row(results=0)]
        train, val, test = _make_splits(rows)
        t, _, _ = encode_categorical_features(train, val, test)
        expected = 2 / 3
        assert abs(t["inspection_type_encoded"].iloc[0] - expected) < 1e-6

    def test_inspection_type_encoded_unseen_val_uses_global_mean(self):
        train_rows = [_base_row(inspection_type="Canvass", results=1)]
        val_rows   = [_base_row(inspection_type="UNSEEN_TYPE", results=0)]
        train, val, test = _make_splits(train_rows, val_rows, val_rows)
        _, v, _ = encode_categorical_features(train, val, test)
        # global mean from train = 1.0
        assert abs(v["inspection_type_encoded"].iloc[0] - 1.0) < 1e-6


    def test_facility_type_encoded_column_added(self):
        train, val, test = _make_splits([_base_row()])
        t, v, e = encode_categorical_features(train, val, test)
        assert "facility_type_encoded" in t.columns

    def test_facility_type_encoded_unseen_val_uses_global_mean(self):
        train_rows = [_base_row(facility_type="Restaurant", results=0)]
        val_rows   = [_base_row(facility_type="UNSEEN_FACILITY", results=0)]
        train, val, test = _make_splits(train_rows, val_rows, val_rows)
        _, v, _ = encode_categorical_features(train, val, test)
        assert abs(v["facility_type_encoded"].iloc[0] - 0.0) < 1e-6


    def test_is_revoked_one_when_license_status_rev(self):
        train, val, test = _make_splits([_base_row(license_status="REV")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["is_revoked"].iloc[0] == 1

    def test_is_revoked_zero_when_license_status_not_rev(self):
        train, val, test = _make_splits([_base_row(license_status="AAC")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["is_revoked"].iloc[0] == 0

    def test_is_revoked_column_is_int(self):
        train, val, test = _make_splits([_base_row()])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["is_revoked"].dtype == int


    def test_application_type_issue_mapped_to_zero(self):
        train, val, test = _make_splits([_base_row(application_type="ISSUE")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["application_type_encoded"].iloc[0] == 0

    def test_application_type_renew_mapped_to_one(self):
        train, val, test = _make_splits([_base_row(application_type="RENEW")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["application_type_encoded"].iloc[0] == 1

    def test_application_type_c_loc_mapped_to_two(self):
        train, val, test = _make_splits([_base_row(application_type="C_LOC")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["application_type_encoded"].iloc[0] == 2

    def test_application_type_unknown_defaults_to_one(self):
        train, val, test = _make_splits([_base_row(application_type="UNKNOWN_TYPE")])
        t, _, _ = encode_categorical_features(train, val, test)
        assert t["application_type_encoded"].iloc[0] == 1


    def test_raw_columns_dropped_from_all_splits(self):
        base = _base_row()
        # add a few NO_LONGER_NEEDED cols that are commonly present
        for col in ["Inspection ID", "License #", "Violations", "Inspection Type",
                    "Facility Type", "LICENSE STATUS", "APPLICATION TYPE"]:
            base[col] = "dummy"
        base["Inspection ID"] = 1
        base["License #"]     = 1
        train, val, test = _make_splits([base])
        t, v, e = encode_categorical_features(train, val, test)
        for col in ["Inspection Type", "Facility Type", "LICENSE STATUS", "APPLICATION TYPE"]:
            assert col not in t.columns
            assert col not in v.columns
            assert col not in e.columns


    def test_val_uses_train_fail_rate_not_its_own(self):
        train_rows = [_base_row(inspection_type="Canvass", results=0),
                      _base_row(inspection_type="Canvass", results=0)]
        val_rows   = [_base_row(inspection_type="Canvass", results=1)]
        train, val, test = _make_splits(train_rows, val_rows, val_rows)
        _, v, _ = encode_categorical_features(train, val, test)
        # train fail rate for Canvass = 0.0, NOT val's 1.0
        assert abs(v["inspection_type_encoded"].iloc[0] - 0.0) < 1e-6


    def test_does_not_mutate_original_dataframes(self):
        train, val, test = _make_splits([_base_row()])
        original_train_cols = list(train.columns)
        encode_categorical_features(train, val, test)
        assert list(train.columns) == original_train_cols