"""
expectations.py
---------------
Build and run the Great Expectations v1.x suite.
Returns a structured results dict so nothing is tied to printing.
"""

from __future__ import annotations

import great_expectations as gx
import pandas as pd


# ── Constants ─────────────────────────────────────────────────────────────────

EXPECTED_COLUMNS = [
    "Inspection ID", "DBA Name", "AKA Name", "License#",
    "Facility Type", "Risk", "Address", "City", "State",
    "Zip", "Inspection Date", "Inspection Type", "Results",
    "Violations", "Latitude", "Longitude", "Location",
]

NOT_NULL_COLUMNS = ["Inspection ID", "DBA Name", "Inspection Date", "Results", "Risk"]


# ── Suite builder ─────────────────────────────────────────────────────────────

def _build_suite() -> gx.ExpectationSuite:
    """Define all expectations and return the suite object."""

    suite = gx.ExpectationSuite(name="inspections_suite")

    # Schema
    suite.add_expectation(
        gx.expectations.ExpectTableColumnsToMatchSet(column_set=EXPECTED_COLUMNS) # type: ignore
    )

    # Completeness
    for col in NOT_NULL_COLUMNS:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column=col) # type: ignore
        )

    # Uniqueness
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(column="Inspection ID") # type: ignore
    )

    # Numeric ranges
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween( # type: ignore
            column="Latitude", min_value=41.6, max_value=42.1
        ) # type: ignore
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween( # type: ignore
            column="Longitude", min_value=-87.9, max_value=-87.5
        )
    )

    # Format
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToMatchRegex(column="Zip", regex=r"^\d{5}$") # type: ignore
    )

    # Categories
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet( # type: ignore
            column="Results",
            value_set=["Pass", "Fail", "Pass w/ Conditions",
                       "Out of Business", "Business Not Located", "No Entry", "Not Ready"],
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet( # type: ignore
            column="Risk",
            value_set=["Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)", "All"],
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(column="State", value_set=["IL"]) # type: ignore
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(column="City", value_set=["CHICAGO"]) # type: ignore
    )

    # Row count sanity
    suite.add_expectation(
        gx.expectations.ExpectTableRowCountToBeBetween(min_value=1_000, max_value=500_000) # type: ignore
    )

    return suite


# ── Results parser ────────────────────────────────────────────────────────────

def _parse_results(raw_results) -> list[dict]:
    """
    Convert raw GX results into a clean list of dicts:
    [{"type": str, "column": str, "passed": bool, "unexpected_count": int, "sample": list}]
    """
    parsed = []
    for exp_result in raw_results.results:
        cfg    = exp_result.expectation_config
        result = exp_result.result or {}
        parsed.append({
            "type":             cfg.type,
            "column":           cfg.kwargs.get("column", "table-level"),
            "passed":           exp_result.success,
            "unexpected_count": result.get("unexpected_count", 0),
            "sample":           result.get("partial_unexpected_list", [])[:3],
        })
    return parsed


# ── Public API ────────────────────────────────────────────────────────────────

def run_gx_validation(df: pd.DataFrame) -> dict:
    """
    Run the full Great Expectations suite against *df*.

    Returns
    -------
    {
        "passed":       bool,
        "pass_count":   int,
        "fail_count":   int,
        "results":      list[dict],   # one dict per expectation
    }
    """
    context    = gx.get_context(mode="ephemeral")
    datasource = context.data_sources.add_pandas(name="source")
    asset      = datasource.add_dataframe_asset(name="asset")
    batch_def  = asset.add_batch_definition_whole_dataframe("batch")

    suite      = context.suites.add(_build_suite())
    val_def    = context.validation_definitions.add(
        gx.ValidationDefinition(name="inspections_validation", data=batch_def, suite=suite)
    )

    raw = val_def.run(batch_parameters={"dataframe": df})
    results = _parse_results(raw)

    return {
        "passed":     raw.success,
        "pass_count": sum(r["passed"] for r in results),
        "fail_count": sum(not r["passed"] for r in results),
        "results":    results,
    }