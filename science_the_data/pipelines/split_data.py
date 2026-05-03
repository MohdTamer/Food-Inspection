"""
pipelines/split_data.py
-----------------------
Temporal train / test split.

Responsibilities
----------------
- Load data from a given stage
- Drop un-dateable rows
- Sort and split by date cutoff
- Assert no temporal / ID leakage
- Trigger EDA figure generation  (drawing only — no report writing)
- Save both splits to the output stage as CSV + Parquet
- Return (train_csv_name, test_csv_name, eda_dict)

Reports are written downstream by ``validations_pipeline``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.pipelines.types import PipelineStage
from science_the_data.eda.eda_split import compute_eda_stats

TARGET_COL = "Results"
DATE_COL = "Inspection Date"
ID_COL = "Inspection ID"

TEST_FRACTION = 0.20

_STAGE_FOLDER: dict[PipelineStage, str] = {
    PipelineStage.RAW:         "raw",
    PipelineStage.INTERIM:     "interim",
    PipelineStage.CLEANED:     "cleaned",
    PipelineStage.PROCESSED:   "processed",
    PipelineStage.QUARANTINED: "quarantined",
}


def splitting_pipeline(
    input_csv_name: str,
    input_stage: PipelineStage,
    output_stage: PipelineStage = PipelineStage.PROCESSED,
    test_fraction: float = TEST_FRACTION,
) -> tuple[str, str, dict]:

    input_path = PathResolver.get_data_path_from_stage(input_csv_name, input_stage)
    df = pd.read_csv(input_path, parse_dates=[DATE_COL])
    logger.info("Loaded '{}' — shape: {}", input_csv_name, df.shape)

    pipeline_logger = PipelineLogger()
    pipeline_logger.log_step(
        step="Initial Load — splitting pipeline",
        rows_before=df.shape[0],
        rows_after=df.shape[0],
        cols_before=df.shape[1],
        cols_after=df.shape[1],
    )

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    null_dates = int(df[DATE_COL].isna().sum())

    if null_dates:
        logger.warning(
            "Dropping {} row(s) with null '{}' ({:.2f}% of data).",
            null_dates, DATE_COL, null_dates / len(df) * 100,
        )
        rows_before_drop = len(df)
        df = df.dropna(subset=[DATE_COL]).copy()
        pipeline_logger.log_step(
            step="Drop null Inspection Dates",
            rows_before=rows_before_drop,
            rows_after=len(df),
            cols_before=df.shape[1],
            cols_after=df.shape[1],
            note=f"{null_dates} rows had no parseable date",
        )

    logger.info(
        "Date range: {} → {}",
        df[DATE_COL].min().date(),
        df[DATE_COL].max().date(),
    )

    df = df.sort_values(DATE_COL).reset_index(drop=True)

    cutoff_idx  = int(len(df) * (1 - test_fraction))
    cutoff_date = df.loc[cutoff_idx, DATE_COL]

    logger.info(
        "Cutoff date: {}  (index {}/{})",
        cutoff_date.date(), cutoff_idx, len(df), # type: ignore
    )

    train_mask = df[DATE_COL] < cutoff_date
    df_train   = df.loc[train_mask].copy()
    df_test    = df.loc[~train_mask].copy()

    for label, subset in [("train", df_train), ("test", df_test)]:
        pipeline_logger.log_step(
            step=f"Temporal split — {label}",
            rows_before=len(df),
            rows_after=len(subset),
            cols_before=df.shape[1],
            cols_after=subset.shape[1],
            note=f"cutoff_date={cutoff_date.date()}", # type: ignore
        )

    logger.info(
        "Train: {:,} rows ({:.1f}%)  |  Test: {:,} rows ({:.1f}%)",
        len(df_train), len(df_train) / len(df) * 100,
        len(df_test),  len(df_test)  / len(df) * 100,
    )

    _assert_no_leakage(df_train, df_test)

    figures_dir = PathResolver.FIGURES / _STAGE_FOLDER[output_stage]
    eda = compute_eda_stats(
        df=df,
        df_train=df_train,
        df_test=df_test,
        cutoff_date=cutoff_date, # type: ignore
        figures_dir=figures_dir,
    )

    train_csv_name, test_csv_name = _save_splits(df_train, df_test, output_stage)

    log_path = Path("logs/splitting.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, test_csv_name, eda

def _assert_no_leakage(df_train: pd.DataFrame, df_test: pd.DataFrame) -> None:
    shared_ids = set(df_train[ID_COL]) & set(df_test[ID_COL])
    assert not shared_ids, (
        f"Leakage: {len(shared_ids)} Inspection ID(s) appear in both splits!"
    )
    assert df_train[DATE_COL].max() < df_test[DATE_COL].min(), (
        "Data leakage: train dates overlap with test dates! "
        f"train_max={df_train[DATE_COL].max().date()}, "
        f"test_min={df_test[DATE_COL].min().date()}"
    )
    logger.info(
        "Leakage checks passed — train max: {}  |  test min: {}",
        df_train[DATE_COL].max().date(),
        df_test[DATE_COL].min().date(),
    )


def _save_splits(
    df_train: pd.DataFrame,
    df_test: pd.DataFrame,
    stage: PipelineStage,
) -> tuple[str, str]:
    train_csv_name = "train.csv"
    test_csv_name  = "test.csv"

    for df_split, csv_name, parq_name in [
        (df_train, train_csv_name, "train.parquet"),
        (df_test,  test_csv_name,  "test.parquet"),
    ]:
        csv_path  = PathResolver.get_data_path_from_stage(csv_name,  stage)
        parq_path = PathResolver.get_data_path_from_stage(parq_name, stage)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        df_split.to_csv(csv_path,   index=False)
        df_split.to_parquet(parq_path, index=False)

        logger.info(
            "Saved {} → {} ({:.1f} MB csv)  +  {} ({:.1f} MB parquet)",
            csv_name,
            csv_path,   csv_path.stat().st_size  / 1e6,
            parq_path,  parq_path.stat().st_size / 1e6,
        )

    return train_csv_name, test_csv_name