from pathlib import Path
from helpers.path_resolver import PathResolver
from loguru import logger
import pandas as pd
from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.pipelines.types import PipelineStage
from science_the_data.cleaning.drop_nulls import drop_fully_nulls_columns, drop_exact_duplicates

def remove_nulls_dups_pipeline(input_csv_name: str, output_stage: PipelineStage) -> str:
    input_path = PathResolver.get_raw_data_path(input_csv_name)
    df = pd.read_csv(input_path, parse_dates=["Inspection Date"])
    df_clean = df.copy()

    pipeline_logger = PipelineLogger()
    pipeline_logger.log_step(
        "Initial Load data into a new dataframe to preserve the RAW data", 
        df.shape[0], 
        df_clean.shape[0], 
        df.shape[1], 
        df_clean.shape[1]
    )
    logger.info("Copied dataframe so as not to touch raw file")

    df_drop_nulls = drop_fully_nulls_columns(df_clean)
    pipeline_logger.log_step(
        "Dropped nulls",
        df_clean.shape[0], 
        df_drop_nulls.shape[0], 
        df_clean.shape[1], 
        df_drop_nulls.shape[1], 
    )
    logger.info("Dropped fully null rows")

    df_drop_exact_duplicates = drop_exact_duplicates(df_drop_nulls)
    pipeline_logger.log_step(
        "Dropped exact Duplicates",
        df_drop_exact_duplicates.shape[0], 
        df_clean.shape[0], 
        df_drop_exact_duplicates.shape[1],
        df_clean.shape[1],
        "Drop fully duplicated rows"
    )
    logger.info("Dropped exact duplicates")

    drop_inspection_id_duplication = drop_fully_nulls_columns(df_clean)
    pipeline_logger.log_step(
        'drop_duplicate_inspection_id', 
        df_drop_exact_duplicates.shape[0], 
        drop_inspection_id_duplication.shape[0], 
        df_drop_exact_duplicates.shape[1], 
        drop_inspection_id_duplication.shape[1], 
        note='Keep latest Inspection Date per Inspection ID'
    )
    logger.info("Dropped records with duplicate inspection_id")

    expected_rows_after_dedup = 196_825
    tolerance = int(expected_rows_after_dedup * 0.05)
    actual_rows_after_dedup = drop_inspection_id_duplication.shape[0]
    logger.info('Shape after duplicate handling:', drop_inspection_id_duplication.shape)
    logger.info(f'Rows after dedup: {actual_rows_after_dedup:,} (expected ~{expected_rows_after_dedup:,} +/- {tolerance:,})')

    path = Path("logs/logs.csv")
    pipeline_logger.save(path)
    logger.info("Saved logs to CSV file in: {}", path)

    cleanedCsvFileName = "cleaned_nulls_dups.csv"

    path = PathResolver.get_data_path_from_stage(cleanedCsvFileName , output_stage)
    drop_inspection_id_duplication.to_csv(path)
    logger.info("Saved cleaned data to CSV file in: {}", path)

    return cleanedCsvFileName
