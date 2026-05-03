from __future__ import annotations

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from science_the_data.helpers.types import PipelineStage, SplitData


def load_splits(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    stage: PipelineStage,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_path = PathResolver.get_data_path_from_stage(train_csv_name, stage)
    val_path   = PathResolver.get_data_path_from_stage(val_csv_name,   stage)
    test_path  = PathResolver.get_data_path_from_stage(test_csv_name,  stage)

    train = pd.read_csv(train_path)
    val   = pd.read_csv(val_path)
    test  = pd.read_csv(test_path)

    logger.info(
        "Loaded train: {} rows | val: {} rows | test: {} rows",
        len(train), len(val), len(test),
    )
    return train, val, test


def save_splits(
    train: SplitData,
    val:   SplitData,
    test:  SplitData,
    stage: PipelineStage,
) -> tuple[str, str, str]:
    for split in [train, val, test]:
        csv_path = PathResolver.get_data_path_from_stage(split.file_name, stage)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        split.df.to_csv(csv_path, index=False)

        logger.info(
            "Saved {} → {} ({:.1f} MB csv)",
            split.file_name, csv_path, csv_path.stat().st_size / 1e6,
        )

    return train.file_name, val.file_name, test.file_name