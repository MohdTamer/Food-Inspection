from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def base_df() -> pd.DataFrame:
    """Minimal DataFrame that resembles the Chicago food-inspection dataset."""
    return pd.DataFrame(
        {
            "Results": ["Pass", "Fail", "Pass", "Pass Out of Business", "Fail"],
            "Inspection Date": pd.to_datetime(
                ["2023-01-10", "2023-03-15", "2023-06-01", "2023-08-20", "2023-11-05"]
            ),
            "Risk": ["Risk 1 (High)", "Risk 2 (Medium)", "Risk 1 (High)", "Risk 3 (Low)", "Risk 2 (Medium)"],
            "Facility Type": ["Restaurant", "Bakery", "Restaurant", "Grocery Store", "Restaurant"],
            "Inspection Type": ["Canvass", "Complaint", "Canvass", "Canvass", "License"],
            "Latitude": [41.85, 41.90, 41.88, None, 41.86],
            "Longitude": [-87.65, -87.70, -87.68, -87.69, -87.67],
            "COMMUNITY AREA NAME": ["Lincoln Park", "Logan Square", "Lincoln Park", "Wicker Park", "Logan Square"],
            "Violations": ["1 | 2 | 3", None, "5 | 6", "7", "2 | 3 | 4 | 5"],
            "score": [10, 20, 30, 40, 50],
        }
    )


@pytest.fixture
def numeric_results_df(base_df) -> pd.DataFrame:
    """base_df with Results encoded as 0/1 for numeric tests."""
    df = base_df.copy()
    df["Results"] = df["Results"].map({"Pass": 0, "Fail": 1, "Pass Out of Business": 0})
    return df