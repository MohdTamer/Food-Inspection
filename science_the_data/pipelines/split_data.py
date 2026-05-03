from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.helpers.types import (SplitData, PipelineStage)
from science_the_data.helpers.splits_io import save_splits
from science_the_data.eda.eda_split import compute_eda_stats

TARGET_COL = "Results"
DATE_COL = "Inspection Date"
ID_COL = "Inspection ID"

TEST_FRACTION = 0.20
VAL_FRACTION  = 0.20

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
    val_fraction: float = VAL_FRACTION,
) -> tuple[str, str, str, dict]:

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
    df_train   = df.loc[train_mask].copy().reset_index(drop=True)
    df_test    = df.loc[~train_mask].copy()

    # Carve validation from the tail of train
    val_cutoff_idx  = int(len(df_train) * (1 - val_fraction))
    val_cutoff_date = df_train.loc[val_cutoff_idx, DATE_COL]
    val_mask        = df_train[DATE_COL] >= val_cutoff_date
    df_val   = df_train.loc[val_mask].copy()
    df_train = df_train.loc[~val_mask].copy()

    logger.info(
        "Val cutoff date: {}  (index {}/{})",
        val_cutoff_date.date(), val_cutoff_idx, len(df_train) + len(df_val), # type: ignore
    )

    for label, subset in [("train", df_train), ("val", df_val), ("test", df_test)]:
        pipeline_logger.log_step(
            step=f"Temporal split — {label}",
            rows_before=len(df),
            rows_after=len(subset),
            cols_before=df.shape[1],
            cols_after=subset.shape[1],
            note=f"test_cutoff={cutoff_date.date()}, val_cutoff={val_cutoff_date.date()}", # type: ignore
        )

    logger.info(
        "Train: {:,} rows ({:.1f}%)  |  Val: {:,} rows ({:.1f}%)  |  Test: {:,} rows ({:.1f}%)",
        len(df_train), len(df_train) / len(df) * 100,
        len(df_val),   len(df_val)   / len(df) * 100,
        len(df_test),  len(df_test)  / len(df) * 100,
    )

    _assert_no_leakage(df_train, df_val, df_test)

    figures_dir = PathResolver.FIGURES / _STAGE_FOLDER[output_stage]
    eda = compute_eda_stats(
        df=df,
        df_train=df_train,
        df_test=df_test,
        cutoff_date=cutoff_date, # type: ignore
        figures_dir=figures_dir,
    )

    train_csv_name, val_csv_name, test_csv_name = "split_train.csv", "split_validation.csv", "split_test.csv"

    save_splits(
        train=SplitData(df=df_train, file_name=train_csv_name),
        val=SplitData(df=df_val,     file_name=val_csv_name),
        test=SplitData(df=df_test,   file_name=test_csv_name),
        stage=output_stage,
    )

    log_path = Path("logs/splitting.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, val_csv_name, test_csv_name, eda

def _assert_no_leakage(
    df_train: pd.DataFrame,
    df_val: pd.DataFrame,
    df_test: pd.DataFrame,
) -> None:
    for a_name, a, b_name, b in [
        ("train", df_train, "val",  df_val),
        ("train", df_train, "test", df_test),
        ("val",   df_val,   "test", df_test),
    ]:
        shared = set(a[ID_COL]) & set(b[ID_COL])
        assert not shared, (
            f"Leakage: {len(shared)} Inspection ID(s) appear in both {a_name} and {b_name}!"
        )

    assert df_train[DATE_COL].max() < df_val[DATE_COL].min(), (
        f"Date overlap: train_max={df_train[DATE_COL].max().date()}, "
        f"val_min={df_val[DATE_COL].min().date()}"
    )

    assert df_train[DATE_COL].max() < df_test[DATE_COL].min(), (
        "Data leakage: train dates overlap with test dates! "
        f"train_max={df_train[DATE_COL].max().date()}, "
    )
    assert df_val[DATE_COL].max() < df_test[DATE_COL].min(), (
        f"Date overlap: val_max={df_val[DATE_COL].max().date()}, "
        f"test_min={df_test[DATE_COL].min().date()}"
    )

    logger.info(
        "Leakage checks passed — train_max: {}  |  val_min: {}  |  val_max: {}  |  test_min: {}",
        df_train[DATE_COL].max().date(),
        df_val[DATE_COL].min().date(),
        df_val[DATE_COL].max().date(),
        df_test[DATE_COL].min().date(),
    )
