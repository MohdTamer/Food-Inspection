from __future__ import annotations

from pathlib import Path

from loguru import logger

from helpers.pipeline_logger import PipelineLogger
from science_the_data.helpers.splits_io import load_splits, save_splits
from science_the_data.pipelines.types import PipelineStage
from transformations.binarize_target import binarize_target


def transformations_pipeline(
    train_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
    output_stage: PipelineStage = PipelineStage.PROCESSED
) -> tuple[str, str]:

    pipeline_logger = PipelineLogger()

    train, test = load_splits(train_csv_name, test_csv_name, input_stage)

    pipeline_logger.log_step(
        step="Initial Load — transformations pipeline",
        rows_before=len(train) + len(test),
        rows_after=len(train) + len(test),
        cols_before=train.shape[1],
        cols_after=train.shape[1],
    )

    train = binarize_target(train)
    test  = binarize_target(test)

    for label, subset in [("train", train), ("test", test)]:
        pipeline_logger.log_step(
            step=f"Binarize target — {label}",
            rows_before=len(subset),
            rows_after=len(subset),
            cols_before=subset.shape[1] + 1,
            cols_after=subset.shape[1],
            note="violation_count dropped; Results binarized",
        )

    train_csv_name = "binary_encoding_train.csv"
    test_csv_name = "binary_encoding_test.csv"

    save_splits(train, train_csv_name, test, test_csv_name, output_stage)

    log_path = Path("logs/transformations.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, test_csv_name

