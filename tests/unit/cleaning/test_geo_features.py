from __future__ import annotations

import pandas as pd
import pytest

from science_the_data.cleaning.geo_features import (
    add_longitude_flag,
    cast_types_and_build_flags,
    normalize_text_fields,
)

class TestNormalizeTextFields:

    def test_strips_and_uppercases_text_columns(self):
        df = pd.DataFrame({"DBA Name": ["  mcdonald's  "], "Address": [" 123 main st "]})
        result = normalize_text_fields(df)
        assert result["DBA Name"].iloc[0] == "MCDONALD'S"
        assert result["Address"].iloc[0] == "123 MAIN ST"

    def test_normalizes_city_to_chicago(self):
        df = pd.DataFrame({"City": ["chicago", "CCHICAGO", "  chicago  "]})
        result = normalize_text_fields(df)
        # City is dropped after flagging — check flag instead
        assert "flag_non_chicago_city" in result.columns
        assert result["flag_non_chicago_city"].sum() == 0

    def test_flags_non_chicago_city(self):
        df = pd.DataFrame({"City": ["CHICAGO", "EVANSTON", "OAK PARK"]})
        result = normalize_text_fields(df)
        assert result["flag_non_chicago_city"].sum() == 2

    def test_flags_non_il_state(self):
        df = pd.DataFrame({"State": ["IL", "NY", "CA"]})
        result = normalize_text_fields(df)
        assert result["flag_non_il_state"].sum() == 2

    def test_does_not_flag_il_state(self):
        df = pd.DataFrame({"State": ["IL", "IL"]})
        result = normalize_text_fields(df)
        assert result["flag_non_il_state"].sum() == 0

    def test_drops_city_and_state_columns(self):
        df = pd.DataFrame({"City": ["CHICAGO"], "State": ["IL"]})
        result = normalize_text_fields(df)
        assert "City" not in result.columns
        assert "State" not in result.columns

    def test_handles_missing_text_columns_gracefully(self):
        df = pd.DataFrame({"some_other_col": [1, 2, 3]})
        result = normalize_text_fields(df)
        assert list(result.columns) == ["some_other_col"]

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame({"Inspection ID": ["123"]})
        cast_types_and_build_flags(df)
        assert df["Inspection ID"].dtype != pd.Int64Dtype()

    def test_handles_null_values_in_text_columns(self):
        df = pd.DataFrame({"DBA Name": [None, "test"]})
        result = normalize_text_fields(df)
        assert pd.isna(result["DBA Name"].iloc[0])
        assert result["DBA Name"].iloc[1] == "TEST"


class TestAddLongitudeFlag:

    def test_flags_longitude_outside_range(self):
        df = pd.DataFrame({"Longitude": [-87.7, -88.0, -87.3]})
        result, flagged = add_longitude_flag(df)
        assert flagged == 2
        assert result["flag_longitude_outside_typical_range"].sum() == 2

    def test_does_not_flag_longitude_inside_range(self):
        df = pd.DataFrame({"Longitude": [-87.7, -87.8, -87.6]})
        result, flagged = add_longitude_flag(df)
        assert flagged == 0

    def test_returns_zero_flagged_when_no_longitude_column(self):
        df = pd.DataFrame({"some_col": [1, 2, 3]})
        result, flagged = add_longitude_flag(df)
        assert flagged == 0
        assert "flag_longitude_outside_typical_range" not in result.columns

    def test_handles_null_longitude_values(self):
        df = pd.DataFrame({"Longitude": [-87.7, None, -88.0]})
        result, flagged = add_longitude_flag(df)
        # null should not be flagged
        assert flagged == 1
        assert result["flag_longitude_outside_typical_range"].iloc[1] == False

    def test_handles_non_numeric_longitude(self):
        df = pd.DataFrame({"Longitude": ["not_a_number", "-87.7"]})
        result, flagged = add_longitude_flag(df)
        # non-numeric coerced to NaN, should not be flagged
        assert result["flag_longitude_outside_typical_range"].iloc[0] == False

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame({"Longitude": [-87.7]})
        add_longitude_flag(df)
        assert "flag_longitude_outside_typical_range" not in df.columns


class TestCastTypesAndBuildFlags:

    def test_casts_int_columns(self):
        df = pd.DataFrame({"Inspection ID": ["123", "456"]})
        result, _ = cast_types_and_build_flags(df)
        assert result["Inspection ID"].dtype == pd.Int64Dtype()

    def test_casts_float_columns(self):
        df = pd.DataFrame({"Latitude": ["41.85", "41.90"]})
        result, _ = cast_types_and_build_flags(df)
        assert result["Latitude"].dtype == float

    def test_casts_date_columns(self):
        df = pd.DataFrame({"Inspection Date": ["2020-01-01", "2021-06-15"]})
        result, _ = cast_types_and_build_flags(df)
        assert pd.api.types.is_datetime64_any_dtype(result["Inspection Date"])

    def test_maps_risk_labels(self):
        df = pd.DataFrame({"Risk": ["Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)"]})
        result, _ = cast_types_and_build_flags(df)
        assert set(result["Risk"]) == {"High", "Medium", "Low"}

    def test_risk_all_becomes_unknown_without_facility_type(self):
        df = pd.DataFrame({"Risk": ["All"]})
        result, _ = cast_types_and_build_flags(df)
        assert result["Risk"].iloc[0] == "Unknown"

    def test_zip_zero_padded(self):
        df = pd.DataFrame({"Zip": ["606", "60614"]})
        result, _ = cast_types_and_build_flags(df)
        assert result["Zip"].iloc[0] == "00606"
        assert result["Zip"].iloc[1] == "60614"

    def test_zip_null_stays_null(self):
        df = pd.DataFrame({"Zip": [None]})
        result, _ = cast_types_and_build_flags(df)
        assert pd.isna(result["Zip"].iloc[0])

    def test_violations_recorded_true_when_violations_present(self):
        df = pd.DataFrame({"Violations": ["1. VIOLATION DESCRIPTION"]})
        result, _ = cast_types_and_build_flags(df)
        assert result["violations_recorded"].iloc[0] == True

    def test_violations_recorded_false_when_violations_empty(self):
        df = pd.DataFrame({"Violations": ["", None]})
        result, _ = cast_types_and_build_flags(df)
        assert result["violations_recorded"].iloc[0] == False
        assert result["violations_recorded"].iloc[1] == False

    def test_license_matched_true_when_bl_license_id_present(self):
        df = pd.DataFrame({"BL_LICENSE_ID": [123, None]})
        result, _ = cast_types_and_build_flags(df)
        assert result["license_matched"].iloc[0] == True
        assert result["license_matched"].iloc[1] == False

    def test_license_matched_false_when_no_license_columns(self):
        df = pd.DataFrame({"some_col": [1, 2]})
        result, _ = cast_types_and_build_flags(df)
        assert result["license_matched"].all() == False

    def test_nulls_leakage_when_license_start_after_inspection(self):
        df = pd.DataFrame({
            "Inspection Date":         pd.to_datetime(["2020-01-01", "2020-06-01"]),
            "LICENSE TERM START DATE": pd.to_datetime(["2021-01-01", "2019-01-01"]),
        })
        result, nulled = cast_types_and_build_flags(df)
        assert nulled == 1
        assert pd.isna(result["LICENSE TERM START DATE"].iloc[0])
        assert result["LICENSE TERM START DATE"].iloc[1] == pd.Timestamp("2019-01-01")

    def test_has_prior_inspection_false_for_first_inspection(self):
        df = pd.DataFrame({
            "License #":       [1, 1, 2],
            "Inspection Date": pd.to_datetime(["2020-01-01", "2021-01-01", "2020-06-01"]),
        })
        result, _ = cast_types_and_build_flags(df)
        grouped = result.sort_values(["License #", "Inspection Date"])
        first_per_license = grouped.groupby("License #").first()
        assert first_per_license["has_prior_inspection"].all() == False

    def test_has_prior_inspection_true_for_subsequent_inspections(self):
        df = pd.DataFrame({
            "License #":       [1, 1],
            "Inspection Date": pd.to_datetime(["2020-01-01", "2021-01-01"]),
        })
        result, _ = cast_types_and_build_flags(df)
        sorted_result = result.sort_values("Inspection Date")
        assert sorted_result["has_prior_inspection"].iloc[1] == True

    def test_location_column_dropped(self):
        df = pd.DataFrame({"Location": ["(41.85, -87.65)"]})
        result, _ = cast_types_and_build_flags(df)
        assert "Location" not in result.columns

    def test_does_not_mutate_original_dataframe(self):
        df = pd.DataFrame({"Inspection ID": ["123"]})
        cast_types_and_build_flags(df)
        assert df["Inspection ID"].dtype != pd.Int64Dtype()