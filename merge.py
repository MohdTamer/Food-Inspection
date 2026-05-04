"""
merge_datasets.py
-----------------
Merges Food Inspections with Business Licenses on license number.

Join key:
  Food Inspections  : "License #"
  Business Licenses : "LICENSE NUMBER"

Strategy: LEFT JOIN — keeps all inspection rows, attaches license metadata where available.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
FOOD_PATH    = Path("data/raw/food-inspections.csv")
LICENSE_PATH = Path("data/raw/Business_Licenses.csv")
OUTPUT_PATH  = Path("data/interim/merged_inspections_licenses_inner.csv")


def load_food_inspections(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    log.info(f"Food Inspections loaded: {df.shape[0]:,} rows × {df.shape[1]} cols")

    # Normalise join key: strip whitespace, cast to nullable Int64
    df["License #"] = (
        df["License #"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)   # remove trailing .0 from float strings
        .replace("nan", pd.NA)
    )
    df["License #"] = pd.to_numeric(df["License #"], errors="coerce").astype("Int64")

    missing_key = df["License #"].isna().sum()
    log.info(f"  Missing 'License #': {missing_key:,} ({missing_key/len(df)*100:.1f}%)")
    return df


def load_business_licenses(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    log.info(f"Business Licenses loaded: {df.shape[0]:,} rows × {df.shape[1]} cols")

    # Normalise join key
    df["LICENSE NUMBER"] = (
        df["LICENSE NUMBER"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .replace("nan", pd.NA)
    )
    df["LICENSE NUMBER"] = pd.to_numeric(df["LICENSE NUMBER"], errors="coerce").astype("Int64")

    missing_key = df["LICENSE NUMBER"].isna().sum()
    log.info(f"  Missing 'LICENSE NUMBER': {missing_key:,} ({missing_key/len(df)*100:.1f}%)")

    # ── De-duplicate Business Licenses ──────────────────────────────────────
    # A single LICENSE NUMBER can appear multiple times (renewals, amendments).
    # Keep the most recent active record per license number to avoid row explosion.
    before = len(df)

    # Prefer ACTIVE status, then most recent DATE ISSUED
    df["DATE ISSUED"] = pd.to_datetime(df["DATE ISSUED"], errors="coerce")

    status_order = {"AAC": 0, "ACT": 1, "REV": 2, "REA": 3}   # lower = more preferred
    df["_status_rank"] = df["LICENSE STATUS"].map(status_order).fillna(99)

    df = (
        df
        .sort_values(["LICENSE NUMBER", "_status_rank", "DATE ISSUED"],
                     ascending=[True, True, False])
        .drop_duplicates(subset=["LICENSE NUMBER"], keep="first")
        .drop(columns=["_status_rank"])
    )

    log.info(f"  Business Licenses after de-dup: {len(df):,} rows (removed {before - len(df):,} duplicates)")
    return df


def merge(food: pd.DataFrame, licenses: pd.DataFrame) -> pd.DataFrame:
    # Rename overlapping columns in licenses before merging to avoid _x/_y suffixes
    rename_map = {
        "LEGAL NAME":                "BL_LEGAL_NAME",
        "DOING BUSINESS AS NAME":    "BL_DBA_NAME",
        "ADDRESS":                   "BL_ADDRESS",
        "CITY":                      "BL_CITY",
        "STATE":                     "BL_STATE",
        "ZIP CODE":                  "BL_ZIP_CODE",
        "LATITUDE":                  "BL_LATITUDE",
        "LONGITUDE":                 "BL_LONGITUDE",
        "LOCATION":                  "BL_LOCATION",
        "LICENSE ID":                "BL_LICENSE_ID",
        "ID":                        "BL_ID",
    }
    licenses = licenses.rename(columns=rename_map)

    merged = food.merge(
        licenses,
        left_on="License #",
        right_on="LICENSE NUMBER",
        how="left",
        suffixes=("", "_BL"),   # fallback suffix if any rename was missed
    )

    matched = merged["LICENSE NUMBER"].notna().sum()
    total   = len(merged)
    log.info(
        f"Merge complete: {total:,} rows | "
        f"matched {matched:,} ({matched/total*100:.1f}%) | "
        f"unmatched {total - matched:,} ({(total - matched)/total*100:.1f}%)"
    )
    log.info(f"Merged shape: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
    return merged


def validation_report(food: pd.DataFrame, licenses: pd.DataFrame, merged: pd.DataFrame) -> None:
    print("\n" + "="*60)
    print("MERGE VALIDATION REPORT")
    print("="*60)

    print(f"\n{'Source':<35} {'Rows':>10} {'Cols':>6}")
    print("-"*55)
    print(f"{'Food Inspections (raw)':<35} {food.shape[0]:>10,} {food.shape[1]:>6}")
    print(f"{'Business Licenses (de-duped)':<35} {licenses.shape[0]:>10,} {licenses.shape[1]:>6}")
    print(f"{'Merged output':<35} {merged.shape[0]:>10,} {merged.shape[1]:>6}")

    matched   = merged["LICENSE NUMBER"].notna().sum()
    unmatched = len(merged) - matched
    print(f"\nMatch rate     : {matched:,} / {len(merged):,} ({matched/len(merged)*100:.2f}%)")
    print(f"Unmatched rows : {unmatched:,} ({unmatched/len(merged)*100:.2f}%)")

    # Row count sanity check (left join must equal food rows)
    assert len(merged) == len(food), (
        f"❌  Row count mismatch after left join: "
        f"expected {len(food):,}, got {len(merged):,}"
    )
    print("\n✅  Row count preserved (left join integrity confirmed)")

    # Duplicate check on join key in merged output
    dup_keys = merged.duplicated(subset=["Inspection ID"]).sum()
    if dup_keys:
        print(f"⚠️   {dup_keys:,} duplicate Inspection IDs in merged output — review license de-dup logic")
    else:
        print("✅  No duplicate Inspection IDs in merged output")

    print("="*60 + "\n")


def main():
    if not FOOD_PATH.exists():
        raise FileNotFoundError(f"Cannot find: {FOOD_PATH}")
    if not LICENSE_PATH.exists():
        raise FileNotFoundError(f"Cannot find: {LICENSE_PATH}")

    food     = load_food_inspections(FOOD_PATH)
    licenses = load_business_licenses(LICENSE_PATH)
    merged   = merge(food, licenses)

    validation_report(food, licenses, merged)

    merged.to_csv(OUTPUT_PATH, index=False)
    log.info(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()