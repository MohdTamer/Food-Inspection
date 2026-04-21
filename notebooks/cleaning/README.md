# Notebook Split Guide

The original `cleaning.ipynb` is now split into smaller notebooks so you can find the relevant step faster.

## Suggested flow
1. `cleaning_01_profile_dedup.ipynb` - raw profiling, null-column removal, duplicate handling, and stage 1 export.
2. `cleaning_02_text_geo_features.ipynb` - city/state normalization, longitude flagging, ZIP/Risk cleanup, leakage fixes, and stage 2 export.
3. `cleaning_03_quarantine_export.ipynb` - quarantine non-trainable labels, final validation, and final exports.

## Outputs
- Stage 1: `../data/interim/cleaning_stage1.csv`
- Stage 2: `../data/interim/cleaning_stage2.csv`
- Final cleaned CSV: `../data/processed/merged_inspections_licenses_inner_clean.csv`
- Final cleaned Parquet: `../data/processed/merged_inspections_licenses_inner_clean.parquet`
- Quarantine rows: `../data/interim/quarantine.csv`
- Logs: `../data/interim/cleaning_stage1_log.csv`, `../data/interim/cleaning_stage2_log.csv`, `../data/interim/cleaning_log.csv`

## Notes
- The notebooks are designed to be run in order.
- The original notebook is still available as a single-file reference if you prefer the full pipeline in one place.
