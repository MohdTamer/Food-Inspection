from pathlib import Path

from loguru import logger
from tqdm import tqdm
import pandas as pd
import typer
from helpers.path_resolver import PathResolver
from helpers.pipeline_logger import PipelineLogger
from science_the_data.cleaning.drop import drop_fully_nulls_columns, drop_exact_duplicates

app = typer.Typer()


@app.command()
def main(
    input_path: Path = PathResolver.raw("merged_inspections_licenses_inner.csv"),
    output_path: Path = PathResolver.processed("output.csv"),
):
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

    path = Path("logs/logs.csv")
    pipeline_logger.save(path)
    logger.info("Saved CSV file to: {}", path)


if __name__ == "__main__":
    app()
