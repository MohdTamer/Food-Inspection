from __future__ import annotations

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from science_the_data.pipelines.types import PipelineStage


def load_splits(
    train_csv_name: str,
    test_csv_name: str,
    stage: PipelineStage,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_path = PathResolver.get_data_path_from_stage(train_csv_name, stage)
    test_path  = PathResolver.get_data_path_from_stage(test_csv_name,  stage)

    train = pd.read_csv(train_path)
    test  = pd.read_csv(test_path)

    logger.info("Loaded train: {} rows | test: {} rows", len(train), len(test))
    return train, test


def save_splits(
    df_train: pd.DataFrame,
    df_train_file_name: str,
    df_test: pd.DataFrame,
    df_test_file_name: str,
    stage: PipelineStage,
) -> tuple[str, str]:
    dataframes_csv_names = [
        (df_train, df_train_file_name),
        (df_test,  df_test_file_name),
    ]

    for df_split, csv_name in dataframes_csv_names:
        csv_path  = PathResolver.get_data_path_from_stage(csv_name,  stage)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        df_split.to_csv(csv_path, index=False)

        logger.info(
            "Saved {} → {} ({:.1f} MB csv)",
            csv_name, csv_path,  csv_path.stat().st_size  / 1e6,
        )

    return df_train_file_name, df_test_file_name