from __future__ import annotations

import pandas as pd

from validations.types import Issue

VALID_RESULTS = frozenset(
    {
        "Pass",
        "Fail",
        "Pass w/ Conditions",
        "Out of Business",
        "Business Not Located",
        "No Entry",
        "Not Ready",
        "1",
        "0",
        0,
        1,  # fe aw2at btshta8al ka number we aw2at string, fa seb el etnen
    }
)

VALID_RISKS = frozenset(
    {
        "Risk 1 (High)",
        "Risk 2 (Medium)",
        "Risk 3 (Low)",
        "All",
        "High",
        "Medium",
        "Low",
        "Unknown",
        "1",
        "2",
        "3",
        1,
        2,
        3,  # fe aw2at btshta8al ka number we aw2at string, fa seb el etnen
    }
)

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
    if "Latitude" not in df.columns:
        return None

    lo, hi = CHICAGO_LAT
    bad = df["Latitude"].dropna()
    bad = bad[(bad < lo) | (bad > hi)]

    if bad.empty:
        return None
    return _issue("Latitude", f"Outside Chicago range [{lo}, {hi}]", len(bad))


def check_longitude(df: pd.DataFrame) -> Issue | None:
    if "Longitude" not in df.columns:
        return None

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


def check_city(df: pd.DataFrame) -> Issue | None:
    if "City" not in df.columns:
        return None

    normalized = df["City"].dropna().str.strip().str.upper()
    bad = normalized[normalized != "CHICAGO"].unique().tolist()

    if not bad:
        return None
    return _issue("City", "Non-CHICAGO values found", len(bad), bad[:5])


def check_state(df: pd.DataFrame) -> Issue | None:
    if "State" not in df.columns:
        return None

    normalized = df["State"].dropna().str.strip().str.upper()
    bad = normalized[normalized != "IL"].unique().tolist()

    if not bad:
        return None
    return _issue("State", "Non-IL values found", len(bad), bad[:5])


def check_zip(df: pd.DataFrame) -> Issue | None:
    if "Zip" not in df.columns:
        return None

    bad = df[~df["Zip"].astype(str).str.match(r"^\d{5}$")]["Zip"].dropna().unique().tolist()

    if not bad:
        return None
    return _issue(
        "Zip", "Malformed zip codes (expected 5 digits)", len(bad), [str(z) for z in bad[:5]]
    )


def check_future_dates(df: pd.DataFrame) -> Issue | None:
    if "Inspection Date" not in df.columns:
        return None

    bad = df[df["Inspection Date"] > pd.Timestamp.today()]

    if bad.empty:
        return None
    return _issue("Inspection Date", "Dates in the future", len(bad))


_ALL_CHECKS = [
    check_results,
    check_risk,
    check_state,
    check_city,
    check_zip,
    check_future_dates,
]


def run_quality_checks(df: pd.DataFrame) -> list[Issue]:
    return [issue for check in _ALL_CHECKS if (issue := check(df)) is not None]
