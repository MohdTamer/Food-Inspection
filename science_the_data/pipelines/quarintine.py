from pathlib import Path

import pandas as pd
from loguru import logger

from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.helpers.types import PipelineStage
from science_the_data.cleaning.quarintine import quarantine_missing_results

def quarantine_pipeline(input_csv_name: str, output_stage: PipelineStage) -> str:
    input_path = PathResolver.get_interim_data_path(input_csv_name)
    df = pd.read_csv(input_path, parse_dates=["Inspection Date"])
    df_clean = df.copy()

    pipeline_logger = PipelineLogger()
    pipeline_logger.log_step(
        "Initial Load data into a new dataframe to preserve the PROCESSED data",
        df.shape[0],
        df_clean.shape[0],
        df.shape[1],
        df_clean.shape[1],
    )
    logger.info("Copied dataframe so as not to touch processed file")

    df_clean, df_quarantined = quarantine_missing_results(df_clean)
    pipeline_logger.log_step(
        "quarantine_missing_results",
        df.shape[0],
        df_clean.shape[0],
        df.shape[1],
        df_clean.shape[1],
        note=f"Quarantined {len(df_quarantined):,} rows with null or empty Results",
    )
    logger.info(
        f"Quarantined {len(df_quarantined):,} rows with missing Results; "
        f"{len(df_clean):,} rows retained"
    )

    log_path = Path("logs/quarantine_log.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log to: {}", log_path)

    if not df_quarantined.empty:
        quarantine_path = PathResolver.get_data_path_from_stage(
            "quarantine.csv", PipelineStage.QUARANTINED
        )
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)
        df_quarantined.to_csv(quarantine_path, index=False)
        logger.info("Saved quarantined rows to: {}", quarantine_path)

    output_csv_name = "clean_final.csv"
    output_path = PathResolver.get_data_path_from_stage(output_csv_name, output_stage)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(output_path, index=False)
    logger.info("Saved clean data to: {}", output_path)

    return output_csv_name