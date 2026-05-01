from pathlib import Path
from loguru import logger
import pandas as pd

from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.pipelines.types import PipelineStage
from science_the_data.cleaning.drop_useless_columns import (
    drop_useless_columns,
    COLS_TO_DROP,
)


def drop_useless_columns_pipeline(input_csv_name: str, output_stage: PipelineStage) -> str:
    input_path = PathResolver.get_data_path_from_stage(input_csv_name, output_stage)
    df = pd.read_csv(input_path, parse_dates=["Inspection Date"])

    pipeline_logger = PipelineLogger()
    pipeline_logger.log_step(
        "Initial Load — drop_useless_columns pipeline",
        df.shape[0],
        df.shape[0],
        df.shape[1],
        df.shape[1],
    )
    logger.info("Loaded '{}' — shape: {}", input_csv_name, df.shape)

    df_dropped = drop_useless_columns(df, COLS_TO_DROP)
    pipeline_logger.log_step(
        "drop_useless_columns",
        df.shape[0],
        df_dropped.shape[0],
        df.shape[1],
        df_dropped.shape[1],
        note="; ".join(COLS_TO_DROP),
    )
    logger.info(
        "Dropped {} column(s): {} → {}",
        df.shape[1] - df_dropped.shape[1],
        df.shape[1],
        df_dropped.shape[1],
    )

    log_path = Path("logs/logs.csv")
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log to: {}", log_path)

    output_csv_name = "cleaned_columns_dropped.csv"
    output_path = PathResolver.get_data_path_from_stage(output_csv_name, output_stage)
    df_dropped.to_csv(output_path, index=False)
    logger.info("Saved output to: {}", output_path)

    return output_csv_name