"""
Data Validation - Version 2: Great Expectations v1.x (Modern API)
==================================================================
Applied Data Science - Cairo University

Works with: great-expectations >= 1.0.0
Install:    pip install great-expectations pandas

The GX 1.x API changed significantly from older versions
"""

import pandas as pd
import numpy as np
import great_expectations as gx
from science_the_data.config import INTERIM_DATA_DIR, RAW_DATA_DIR


# ─────────────────────────────────────────────
# SECTION 1: BASIC STATISTICS REPORT
# ─────────────────────────────────────────────

def print_basic_stats(df: pd.DataFrame):
    """Print row/column counts, data types, missing values, and duplicates."""

    print("\n" + "=" * 58)
    print("    BASIC DATASET STATISTICS")
    print("=" * 58)

    # Row / Column counts
    print(f"\n  Rows    : {df.shape[0]:,}")
    print(f"  Columns : {df.shape[1]}")

    # Data types
    print("\n" + "-" * 58)
    print("  COLUMN DATA TYPES")
    print("-" * 58)
    for col, dtype in df.dtypes.items():
        print(f"  {col:<30} {str(dtype)}")

    # Missing values
    print("\n" + "-" * 58)
    print("  MISSING VALUES")
    print("-" * 58)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_pct
    })
    missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values("Missing Count", ascending=False)

    if missing_df.empty:
        print("  No missing values found.")
    else:
        for col, row in missing_df.iterrows():
            print(f"  {col:<30} {int(row['Missing Count']):>6,} missing  ({row['Missing %']}%)")

    # Duplicates
    print("\n" + "-" * 58)
    print("  DUPLICATES")
    print("-" * 58)
    full_dupes = df.duplicated().sum()
    id_dupes   = df.duplicated(subset=["Inspection ID"]).sum()
    print(f"  Fully duplicate rows     : {full_dupes:,}")
    print(f"  Duplicate Inspection IDs : {id_dupes:,}")

    print("\n" + "=" * 58)


# ─────────────────────────────────────────────
# SECTION 2: QUALITY ISSUES REPORT
# ─────────────────────────────────────────────

def print_quality_issues(df: pd.DataFrame):
    """Check for common data quality issues and print a summary."""

    print("\n" + "=" * 58)
    print("    DATA QUALITY ISSUES")
    print("=" * 58)

    issues_found = False

    # Latitude out of Chicago range
    lat_issues = df["Latitude"].dropna()
    lat_out = lat_issues[(lat_issues < 41.6) | (lat_issues > 42.1)]
    if not lat_out.empty:
        print(f"\n  [!] Latitude out of Chicago range : {len(lat_out):,} rows")
        issues_found = True

    # Longitude out of Chicago range
    lon_issues = df["Longitude"].dropna()
    lon_out = lon_issues[(lon_issues < -87.9) | (lon_issues > -87.5)]
    if not lon_out.empty:
        print(f"  [!] Longitude out of Chicago range : {len(lon_out):,} rows")
        issues_found = True

    # Unexpected Results values
    valid_results = {"Pass", "Fail", "Pass w/ Conditions", "Out of Business",
                     "Business Not Located", "No Entry", "Not Ready"}
    bad_results = df[~df["Results"].isin(valid_results)]["Results"].unique()
    if len(bad_results) > 0:
        print(f"  [!] Unexpected Results values : {bad_results}")
        issues_found = True

    # Unexpected Risk values
    valid_risks = {"Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)", "All"}
    bad_risks = df[~df["Risk"].isin(valid_risks)]["Risk"].dropna().unique()
    if len(bad_risks) > 0:
        print(f"  [!] Unexpected Risk values : {bad_risks}")
        issues_found = True

    # State is not IL
    bad_states = df[df["State"] != "IL"]["State"].dropna().unique()
    if len(bad_states) > 0:
        print(f"  [!] Unexpected State values : {bad_states}")
        issues_found = True

    # City is not CHICAGO
    bad_cities = df[df["City"].str.upper() != "CHICAGO"]["City"].dropna().unique()
    if len(bad_cities) > 0:
        print(f"  [!] Unexpected City values ({len(bad_cities)} unique) : {bad_cities[:5]}")
        issues_found = True

    # Zip not 5 digits
    bad_zips = df[~df["Zip"].astype(str).str.match(r"^\d{5}$")]["Zip"].dropna().unique()
    if len(bad_zips) > 0:
        print(f"  [!] Malformed Zip codes : {bad_zips[:5]}")
        issues_found = True

    # Inspection Date in the future
    future_dates = df[df["Inspection Date"] > pd.Timestamp.today()]
    if not future_dates.empty:
        print(f"  [!] Inspection Dates in the future : {len(future_dates):,} rows")
        issues_found = True

    if not issues_found:
        print("\n  No quality issues detected.")

    print("\n" + "=" * 58)


# ─────────────────────────────────────────────
# SECTION 3: GREAT EXPECTATIONS VALIDATION
# ─────────────────────────────────────────────

def run_validation(df: pd.DataFrame):
    """
    Run data validation using Great Expectations v1.x API.
    """

    # Step 1: Create an in-memory GX context (no files written to disk)
    context = gx.get_context(mode="ephemeral")

    # Step 2: Connect GX to your pandas DataFrame
    data_source = context.data_sources.add_pandas(name="inspections_pandas_source")
    data_asset  = data_source.add_dataframe_asset(name="inspections_asset")
    batch_def   = data_asset.add_batch_definition_whole_dataframe("my_batch")
    batch       = batch_def.get_batch(batch_parameters={"dataframe": df})

    # Step 3: Create an Expectation Suite
    suite = context.suites.add(
        gx.ExpectationSuite(name="inspections_validation_suite")
    )

    # ── DIMENSION 1: SCHEMA ───────────────────────────────────────────────
    suite.add_expectation(
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=[
                "Inspection ID", "DBA Name", "AKA Name", "License#",
                "Facility Type", "Risk", "Address", "City", "State",
                "Zip", "Inspection Date", "Inspection Type", "Results",
                "Violations", "Latitude", "Longitude", "Location"
            ]
        )
    )

    # ── DIMENSION 2: COMPLETENESS ─────────────────────────────────────────
    for col in ["Inspection ID", "DBA Name", "Inspection Date", "Results", "Risk"]:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column=col)
        )

    # ── DIMENSION 3: UNIQUENESS ───────────────────────────────────────────
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(column="Inspection ID")
    )

    # ── DIMENSION 4: ACCURACY ─────────────────────────────────────────────
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="Latitude", min_value=41.6, max_value=42.1
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="Longitude", min_value=-87.9, max_value=-87.5
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToMatchRegex(
            column="Zip", regex=r"^\d{5}$"
        )
    )

    # ── DIMENSION 5: CATEGORICAL ──────────────────────────────────────────
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="Results",
            value_set=["Pass", "Fail", "Pass w/ Conditions", "Out of Business",
                       "Business Not Located", "No Entry", "Not Ready"]
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="Risk",
            value_set=["Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)", "All"]
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="State",
            value_set=["IL"]
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="City",
            value_set=["CHICAGO"]
        )
    )

    # ── DIMENSION 6: DISTRIBUTION ─────────────────────────────────────────
    suite.add_expectation(
        gx.expectations.ExpectTableRowCountToBeBetween(
            min_value=1000, max_value=500000
        )
    )

    # Step 4: Validation Definition
    validation_def = context.validation_definitions.add(
        gx.ValidationDefinition(
            name="inspections_validation",
            data=batch_def,
            suite=suite
        )
    )

    # Step 5: Run
    results = validation_def.run(batch_parameters={"dataframe": df})

    # Step 6: Print GX report
    _print_gx_report(results)

    context.build_data_docs()
    context.open_data_docs()

    return results


def _print_gx_report(results):
    """Print a clean summary of GX v1.x validation results."""

    success = results.success

    print("\n" + "=" * 58)
    print("    GREAT EXPECTATIONS VALIDATION REPORT")
    print("=" * 58)
    print(f"  Overall Result : {'✓ PASSED' if success else '✗ FAILED'}")
    print("=" * 58)

    passed_count = 0
    failed_count = 0

    for exp_result in results.results:
        exp_type = exp_result.expectation_config.type
        col      = exp_result.expectation_config.kwargs.get("column", "table-level")
        passed   = exp_result.success
        status   = "PASS" if passed else "FAIL"

        if passed:
            passed_count += 1
        else:
            failed_count += 1

        print(f"\n  [{status}] {exp_type}")
        print(f"   Column : {col}")

        if not passed and exp_result.result:
            r = exp_result.result
            if r.get("unexpected_count"):
                print(f"   Issues : {r['unexpected_count']:,} unexpected values")
            if r.get("partial_unexpected_list"):
                print(f"   Sample : {r['partial_unexpected_list'][:3]}")

    print("\n" + "-" * 58)
    print(f"  Passed : {passed_count}  |  Failed : {failed_count}  |  Total : {passed_count + failed_count}")
    print("=" * 58)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    df = pd.read_csv(INTERIM_DATA_DIR / 'merged_inspections_licenses_inner.csv', parse_dates=['Inspection Date'])

    print_basic_stats(df)       # Row/col counts, dtypes, missing, duplicates
    print_quality_issues(df)    # Domain-specific quality checks
    run_validation(df)          # Great Expectations formal validation