from pathlib import Path

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.helpers.types import PipelineStage
from science_the_data.cleaning.geo_features import (
    normalize_text_fields,
    add_longitude_flag,
    cast_types_and_build_flags,
)


def geo_blocking_pipeline(input_csv_name: str, output_stage: PipelineStage) -> str:
    input_path = PathResolver.get_interim_data_path(input_csv_name)
    df = pd.read_csv(input_path, parse_dates=["Inspection Date"])
    df_clean = df.copy()

    pipeline_logger = PipelineLogger()
    pipeline_logger.log_step(
        "Initial Load data into a new dataframe to preserve the INTERIM data",
        df.shape[0],
        df_clean.shape[0],
        df.shape[1],
        df_clean.shape[1],
    )
    logger.info("Copied dataframe so as not to touch interim file")

    df_text_normalized = normalize_text_fields(df_clean)
    pipeline_logger.log_step(
        "normalize_text_fields_and_flags",
        df_clean.shape[0],
        df_text_normalized.shape[0],
        df_clean.shape[1],
        df_text_normalized.shape[1],
        note="Normalize text, add city/state flags, drop City/State",
    )
    logger.info("Normalized text fields and added city/state anomaly flags")

    df_lon_flagged, lon_flagged_count = add_longitude_flag(df_text_normalized)
    pipeline_logger.log_step(
        "add_longitude_flag",
        df_text_normalized.shape[0],
        df_lon_flagged.shape[0],
        df_text_normalized.shape[1],
        df_lon_flagged.shape[1],
        note=f"Flagged {lon_flagged_count:,} longitude values outside [-87.95, -87.5]",
    )
    logger.info(f"Flagged {lon_flagged_count:,} longitude anomalies")

    df_cast, nulled_leakage = cast_types_and_build_flags(df_lon_flagged)
    pipeline_logger.log_step(
        "cast_types_and_build_flags",
        df_lon_flagged.shape[0],
        df_cast.shape[0],
        df_lon_flagged.shape[1],
        df_cast.shape[1],
        note=(
            f"Type casting, Risk standardisation, leakage fix "
            f"({nulled_leakage:,} rows nulled), informative flags, drop Location"
        ),
    )
    logger.info(f"Cast types, standardised Risk, nulled {nulled_leakage:,} leakage rows, built flags")

    log_path = Path("logs/geo_blocking_log.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log to: {}", log_path)

    output_csv_name = "geo_blocked.csv"
    output_path = PathResolver.get_data_path_from_stage(output_csv_name, output_stage)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_cast.to_csv(output_path, index=False)
    logger.info("Saved cleaned data to: {}", output_path)

    return output_csv_name