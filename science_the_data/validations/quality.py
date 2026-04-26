from __future__ import annotations

import pandas as pd

from validations.types import Issue 

VALID_RESULTS = frozenset({
    "Pass", "Fail", "Pass w/ Conditions",
    "Out of Business", "Business Not Located", "No Entry", "Not Ready",
})

VALID_RISKS = frozenset({
    "Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)", "All",
})

CHICAGO_LAT = (41.6, 42.1)
CHICAGO_LON = (-87.9, -87.5)

def _issue(field: str, message: str, count: int, sample: list | None = None) -> Issue:
    return {
        "field": field,
        "message": message,
        "count": count,
        "sample": sample or [],
    }

def check_latitude(df: pd.DataFrame) -> Issue | None:
    lo, hi = CHICAGO_LAT
    bad = df["Latitude"].dropna()
    bad = bad[(bad < lo) | (bad > hi)]

    if bad.empty:
        return None
    return _issue("Latitude", f"Outside Chicago range [{lo}, {hi}]", len(bad))


def check_longitude(df: pd.DataFrame) -> Issue | None:
    lo, hi = CHICAGO_LON
    bad = df["Longitude"].dropna()
    bad = bad[(bad < lo) | (bad > hi)]

    if bad.empty:
        return None
    return _issue("Longitude", f"Outside Chicago range [{lo}, {hi}]", len(bad))


def check_results(df: pd.DataFrame) -> Issue | None:
    bad = df[~df["Results"].isin(VALID_RESULTS)]["Results"].unique().tolist()

    if not bad:
        return None
    return _issue("Results", "Unexpected category values", len(bad), bad[:5])


def check_risk(df: pd.DataFrame) -> Issue | None:
    bad = df[~df["Risk"].isin(VALID_RISKS)]["Risk"].dropna().unique().tolist()

    if not bad:
        return None
    return _issue("Risk", "Unexpected category values", len(bad), bad[:5])


def check_state(df: pd.DataFrame) -> Issue | None:
    bad = df[df["State"] != "IL"]["State"].dropna().unique().tolist()

    if not bad:
        return None
    return _issue("State", "Non-IL values found", len(bad), bad[:5])


def check_city(df: pd.DataFrame) -> Issue | None:
    bad = df[df["City"].str.upper() != "CHICAGO"]["City"].dropna().unique().tolist()

    if not bad:
        return None
    return _issue("City", f"Non-CHICAGO values found ({len(bad)} unique)", len(bad), bad[:5])


def check_zip(df: pd.DataFrame) -> Issue | None:
    bad = df[~df["Zip"].astype(str).str.match(r"^\d{5}$")]["Zip"].dropna().unique().tolist()

    if not bad:
        return None
    return _issue("Zip", "Malformed zip codes (expected 5 digits)", len(bad), [str(z) for z in bad[:5]])


def check_future_dates(df: pd.DataFrame) -> Issue | None:
    bad = df[df["Inspection Date"] > pd.Timestamp.today()]

    if bad.empty:
        return None
    return _issue("Inspection Date", "Dates in the future", len(bad))


_ALL_CHECKS = [
    check_latitude,
    check_longitude,
    check_results,
    check_risk,
    check_state,
    check_city,
    check_zip,
    check_future_dates,
]


def run_quality_checks(df: pd.DataFrame) -> list[Issue]:
    return [issue for check in _ALL_CHECKS if (issue := check(df)) is not None]