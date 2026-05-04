from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.transformations.feature_engineering import (
    RISK_MAP,
    apply_feature_engineering,
    encode_risk,
    engineer_license_expiry,
    parse_dates,
)


def _make_splits(rows: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(rows)
    return df.copy(), df.copy(), df.copy()


def _base_risk_row(risk: str = "High") -> dict:
    return {"Risk": risk}


def _base_date_row(
    inspection_date: str = "2020-01-01",
    expiry_date: str     = "2022-01-01",
    start_date: str      = "2019-01-01",
) -> dict:
    return {
        "Inspection Date":              inspection_date,
        "LICENSE TERM EXPIRATION DATE": expiry_date,
        "LICENSE TERM START DATE":      start_date,
    }


class TestEncodeRisk:

    def test_high_risk_mapped_to_three(self):
        t, v, e = _make_splits([_base_risk_row("High")])
        t, _, _ = encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == 3

    def test_medium_risk_mapped_to_two(self):
        t, v, e = _make_splits([_base_risk_row("Medium")])
        t, _, _ = encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == 2

    def test_low_risk_mapped_to_one(self):
        t, v, e = _make_splits([_base_risk_row("Low")])
        t, _, _ = encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == 1

    def test_unknown_risk_mapped_to_three(self):
        t, v, e = _make_splits([_base_risk_row("Unknown")])
        t, _, _ = encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == 3

    def test_all_splits_are_encoded(self):
        t, v, e = _make_splits([_base_risk_row("Low")])
        t, v, e = encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == 1
        assert v["Risk"].iloc[0] == 1
        assert e["Risk"].iloc[0] == 1

    def test_does_not_mutate_original(self):
        t, v, e = _make_splits([_base_risk_row("High")])
        original = t["Risk"].iloc[0]
        encode_risk(t, v, e)
        assert t["Risk"].iloc[0] == original


class TestParseDates:

    def test_inspection_date_parsed_to_datetime(self):
        t, v, e = _make_splits([_base_date_row()])
        t, _, _ = parse_dates(t, v, e)
        assert pd.api.types.is_datetime64_any_dtype(t["Inspection Date"])

    def test_expiry_date_parsed_to_datetime(self):
        t, v, e = _make_splits([_base_date_row()])
        t, _, _ = parse_dates(t, v, e)
        assert pd.api.types.is_datetime64_any_dtype(t["LICENSE TERM EXPIRATION DATE"])

    def test_start_date_parsed_to_datetime(self):
        t, v, e = _make_splits([_base_date_row()])
        t, _, _ = parse_dates(t, v, e)
        assert pd.api.types.is_datetime64_any_dtype(t["LICENSE TERM START DATE"])

    def test_invalid_date_coerced_to_nat(self):
        t, v, e = _make_splits([{"Inspection Date": "not_a_date",
                                  "LICENSE TERM EXPIRATION DATE": "2022-01-01",
                                  "LICENSE TERM START DATE": "2019-01-01"}])
        t, _, _ = parse_dates(t, v, e)
        assert pd.isna(t["Inspection Date"].iloc[0])

    def test_missing_date_column_skipped_gracefully(self):
        t, v, e = _make_splits([{"Risk": "High"}])
        # should not raise even though date cols are absent
        t, _, _ = parse_dates(t, v, e)
        assert "Inspection Date" not in t.columns

    def test_does_not_mutate_original(self):
        t, v, e = _make_splits([_base_date_row()])
        original_dtype = t["Inspection Date"].dtype
        parse_dates(t, v, e)
        assert t["Inspection Date"].dtype == original_dtype


class TestEngineerLicenseExpiry:

    def _date_df(self, inspection: str, expiry: str) -> pd.DataFrame:
        return pd.DataFrame({
            "Inspection Date":              pd.to_datetime([inspection]),
            "LICENSE TERM EXPIRATION DATE": pd.to_datetime([expiry]),
        })

    def test_days_to_license_expiry_computed_correctly(self):
        df = self._date_df("2020-01-01", "2022-01-01")
        t, v, e = engineer_license_expiry(df.copy(), df.copy(), df.copy())
        assert t["days_to_license_expiry"].iloc[0] == 731

    def test_days_to_license_expiry_column_added(self):
        df = self._date_df("2020-01-01", "2022-01-01")
        t, _, _ = engineer_license_expiry(df.copy(), df.copy(), df.copy())
        assert "days_to_license_expiry" in t.columns

    def test_license_expiry_missing_flag_one_when_null(self):
        df = pd.DataFrame({
            "Inspection Date":              pd.to_datetime(["2020-01-01"]),
            "LICENSE TERM EXPIRATION DATE": [pd.NaT],
        })
        t, _, _ = engineer_license_expiry(df.copy(), df.copy(), df.copy())
        assert t["license_expiry_missing"].iloc[0] == 1

    def test_license_expiry_missing_flag_zero_when_not_null(self):
        df = self._date_df("2020-01-01", "2022-01-01")
        t, _, _ = engineer_license_expiry(df.copy(), df.copy(), df.copy())
        assert t["license_expiry_missing"].iloc[0] == 0

    def test_null_expiry_filled_with_train_median(self):
        train = pd.DataFrame({
            "Inspection Date":              pd.to_datetime(["2020-01-01", "2020-01-01"]),
            "LICENSE TERM EXPIRATION DATE": pd.to_datetime(["2022-01-01", "2023-01-01"]),
        })
        val = pd.DataFrame({
            "Inspection Date":              pd.to_datetime(["2020-01-01"]),
            "LICENSE TERM EXPIRATION DATE": [pd.NaT],
        })
        t, v, e = engineer_license_expiry(train.copy(), val.copy(), val.copy())
        # train median = (731 + 1096) / 2 = 913.5
        assert not pd.isna(v["days_to_license_expiry"].iloc[0])

    def test_no_nulls_remain_after_fill(self):
        train = self._date_df("2020-01-01", "2022-01-01")
        val = pd.DataFrame({
            "Inspection Date":              pd.to_datetime(["2020-01-01"]),
            "LICENSE TERM EXPIRATION DATE": [pd.NaT],
        })
        t, v, e = engineer_license_expiry(train.copy(), val.copy(), val.copy())
        assert v["days_to_license_expiry"].isna().sum() == 0

    def test_does_not_mutate_original(self):
        df = self._date_df("2020-01-01", "2022-01-01")
        original_cols = list(df.columns)
        engineer_license_expiry(df.copy(), df.copy(), df.copy())
        assert list(df.columns) == original_cols


class TestApplyFeatureEngineering:

    def test_returns_three_dataframes(self):
        rows = [{
            "Risk":                         "High",
            "Inspection Date":              "2020-01-01",
            "LICENSE TERM EXPIRATION DATE": "2022-01-01",
            "LICENSE TERM START DATE":      "2019-01-01",
        }]
        t, v, e = _make_splits(rows)
        result = apply_feature_engineering(t, v, e)
        assert len(result) == 3

    def test_all_feature_columns_present(self):
        rows = [{
            "Risk":                         "High",
            "Inspection Date":              "2020-01-01",
            "LICENSE TERM EXPIRATION DATE": "2022-01-01",
            "LICENSE TERM START DATE":      "2019-01-01",
        }]
        t, v, e = _make_splits(rows)
        t, v, e = apply_feature_engineering(t, v, e)
        assert "days_to_license_expiry" in t.columns
        assert "license_expiry_missing" in t.columns
        assert pd.api.types.is_datetime64_any_dtype(t["Inspection Date"])