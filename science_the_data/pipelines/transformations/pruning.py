from __future__ import annotations

from pathlib import Path

from loguru import logger

from helpers.pipeline_logger import PipelineLogger
from helpers.splits_io import load_splits, save_splits
from science_the_data.helpers.types import PipelineStage, SplitData
from transformations.pruning import prune_columns


def pruning_pipeline(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
    output_stage: PipelineStage = PipelineStage.PROCESSED,
) -> tuple[str, str, str]:
    pipeline_logger = PipelineLogger()

    train, val, test = load_splits(train_csv_name, val_csv_name, test_csv_name, input_stage)

    pipeline_logger.log_step(
        step="Initial Load — pruning pipeline",
        rows_before=len(train) + len(val) + len(test),
        rows_after=len(train) + len(val) + len(test),
        cols_before=train.shape[1],
        cols_after=train.shape[1],
    )

    cols_before = train.shape[1]

    train, dropped_train = prune_columns(train)
    val, _ = prune_columns(val)
    test, _ = prune_columns(test)

    cols_after = train.shape[1]

    for label, subset in [("train", train), ("val", val), ("test", test)]:
        pipeline_logger.log_step(
            step=f"Prune columns — {label}",
            rows_before=len(subset),
            rows_after=len(subset),
            cols_before=cols_before,
            cols_after=cols_after,
            note=f"Dropped {len(dropped_train)} column(s): {dropped_train}",
        )

    train_csv_name = "pruned_train.csv"
    val_csv_name = "pruned_val.csv"
    test_csv_name = "pruned_test.csv"

    train_csv_name, val_csv_name, test_csv_name = save_splits(
        train=SplitData(df=train, file_name=train_csv_name),
        val=SplitData(df=val, file_name=val_csv_name),
        test=SplitData(df=test, file_name=test_csv_name),
        stage=output_stage,
    )

    log_path = Path("logs/pruning.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, val_csv_name, test_csv_name
