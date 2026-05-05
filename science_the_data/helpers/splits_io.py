from __future__ import annotations

from loguru import logger
import pandas as pd

from science_the_data.helpers.path_resolver import PathResolver
from science_the_data.helpers.types import PipelineStage, SplitData


def _csv_to_parquet_path(csv_path) -> object:
    return csv_path.with_suffix(".parquet")


def load_splits(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    stage: PipelineStage,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    def _load(csv_name: str) -> pd.DataFrame:
        csv_path = PathResolver.get_data_path_from_stage(csv_name, stage)
        parq_path = _csv_to_parquet_path(csv_path)

        if parq_path.exists():  # type: ignore
            logger.info("Reading parquet → {}", parq_path)
            return pd.read_parquet(parq_path)  # type: ignore

        logger.info("Parquet not found, falling back to csv → {}", csv_path)
        return pd.read_csv(csv_path)

    train = _load(train_csv_name)
    val = _load(val_csv_name)
    test = _load(test_csv_name)

    logger.info(
        "Loaded train: {} rows | val: {} rows | test: {} rows",
        len(train),
        len(val),
        len(test),
    )
    return train, val, test


def save_splits(
    train: SplitData,
    val: SplitData,
    test: SplitData,
    stage: PipelineStage,
) -> tuple[str, str, str]:

    def _save(split: SplitData) -> None:
        csv_path = PathResolver.get_data_path_from_stage(split.file_name, stage)
        parq_path = _csv_to_parquet_path(csv_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        split.df.to_csv(csv_path, index=False)
        split.df.to_parquet(parq_path, index=False)  # type: ignore

        logger.info(
            "Saved {} → csv ({:.1f} MB) + parquet ({:.1f} MB)",
            split.file_name,
            csv_path.stat().st_size / 1e6,
            parq_path.stat().st_size / 1e6,  # type: ignore
        )

    _save(train)
    _save(val)
    _save(test)

    return train.file_name, val.file_name, test.file_name
