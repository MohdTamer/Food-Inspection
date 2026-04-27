from __future__ import annotations

import pandas as pd

_TEXT_COLS = ["City", "State", "DBA Name", "AKA Name", "Address"]

_LON_LO = -87.95
_LON_HI = -87.5

_INT_COLS = [
    "Inspection ID", "License #", "LICENSE NUMBER", "BL_LICENSE_ID",
    "ACCOUNT NUMBER", "SITE NUMBER", "WARD", "PRECINCT", "POLICE DISTRICT",
    "COMMUNITY AREA", "LICENSE CODE", "SSA", "BL_ZIP_CODE",
]
_FLOAT_COLS = ["Latitude", "Longitude", "BL_LATITUDE", "BL_LONGITUDE"]
_DATE_COLS = [
    "Inspection Date", "APPLICATION CREATED DATE",
    "APPLICATION REQUIREMENTS COMPLETE", "PAYMENT DATE",
    "LICENSE TERM START DATE", "LICENSE TERM EXPIRATION DATE",
    "LICENSE APPROVED FOR ISSUANCE", "DATE ISSUED", "LICENSE STATUS CHANGE DATE",
]
_PRIOR_KEY_CANDIDATES = [
    "BL_LICENSE_ID", "License #", "LICENSE NUMBER", "DBA Name", "AKA Name",
]


def normalize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in _TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().str.upper()

    if "City" in df.columns:
        df["City"] = (
            df["City"]
            .str.upper()
            .str.replace(r"\s+", " ", regex=True)
            .str.replace(r"^C+HICAGO$", "CHICAGO", regex=True)
        )

    if "State" in df.columns:
        df["flag_non_il_state"] = df["State"].notna() & (df["State"] != "IL")
    if "City" in df.columns:
        df["flag_non_chicago_city"] = df["City"].notna() & (df["City"] != "CHICAGO")

    drop_geo_cols = [c for c in ["City", "State"] if c in df.columns]
    if drop_geo_cols:
        df = df.drop(columns=drop_geo_cols)

    return df


def add_longitude_flag(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    df = df.copy()
    flagged = 0

    if "Longitude" in df.columns:
        lon = pd.to_numeric(df["Longitude"], errors="coerce")
        df["flag_longitude_outside_typical_range"] = lon.notna() & (
            (lon < _LON_LO) | (lon > _LON_HI)
        )
        flagged = int(df["flag_longitude_outside_typical_range"].sum())

    return df, flagged


def cast_types_and_build_flags(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    df = df.copy()

    for col in _INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")

    for col in _FLOAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in _DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "Zip" in df.columns:
        zip_num = pd.to_numeric(df["Zip"], errors="coerce")
        df["Zip"] = zip_num.astype("Int64").astype("string").str.zfill(5)
        df.loc[zip_num.isna(), "Zip"] = pd.NA

    if "Risk" in df.columns:
        risk_map = {
            "Risk 1 (High)": "High",
            "Risk 2 (Medium)": "Medium",
            "Risk 3 (Low)": "Low",
            "All": pd.NA,
        }
        risk = df["Risk"].astype("string").str.strip().replace(risk_map)
        if "Facility Type" in df.columns:
            mode_by_facility = risk.groupby(df["Facility Type"]).transform(
                lambda s: s.dropna().mode().iloc[0] if not s.dropna().empty else pd.NA
            )
            risk = risk.fillna(mode_by_facility)
        df["Risk"] = risk.fillna("Unknown")

    nulled_leakage = 0
    if {"Inspection Date", "LICENSE TERM START DATE"}.issubset(df.columns):
        mask = (
            df["Inspection Date"].notna()
            & df["LICENSE TERM START DATE"].notna()
            & (df["LICENSE TERM START DATE"] > df["Inspection Date"])
        )
        df.loc[mask, "LICENSE TERM START DATE"] = pd.NaT
        nulled_leakage = int(mask.sum())

    if "Violations" in df.columns:
        violations_str = df["Violations"].astype("string").str.strip()
        df["violations_recorded"] = violations_str.notna() & violations_str.ne("")

    if "BL_LICENSE_ID" in df.columns:
        df["license_matched"] = df["BL_LICENSE_ID"].notna()
    elif "LICENSE NUMBER" in df.columns:
        df["license_matched"] = df["LICENSE NUMBER"].notna()
    else:
        df["license_matched"] = False

    if "Inspection Date" in df.columns:
        prior_key = next(
            (c for c in _PRIOR_KEY_CANDIDATES if c in df.columns), None
        )
        if prior_key is not None:
            ordered_idx = df.sort_values([prior_key, "Inspection Date"]).index
            cumcount = (
                df.loc[ordered_idx]
                .groupby(prior_key)
                .cumcount()
                .gt(0)
                .to_numpy()
            )
            has_prior = pd.Series(False, index=df.index)
            has_prior.loc[ordered_idx] = cumcount
            df["has_prior_inspection"] = has_prior
        else:
            df["has_prior_inspection"] = False

    if "Location" in df.columns:
        df = df.drop(columns=["Location"])

    return df, nulled_leakage