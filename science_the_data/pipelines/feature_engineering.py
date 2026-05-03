from pathlib import Path

from loguru import logger

from helpers.pipeline_logger import PipelineLogger
from helpers.splits_io import load_splits, save_splits
from science_the_data.pipelines.types import PipelineStage
from transformations.feature_engineering import apply_feature_engineering


def feature_engineering_pipeline(
    train_csv_name: str,
    test_csv_name: str,
    stage: PipelineStage = PipelineStage.PROCESSED,
) -> tuple[str, str]:

    pipeline_logger = PipelineLogger()

    train, test = load_splits(train_csv_name, test_csv_name, stage)

    pipeline_logger.log_step(
        step="Initial Load — feature engineering pipeline",
        rows_before=len(train) + len(test),
        rows_after=len(train) + len(test),
        cols_before=train.shape[1],
        cols_after=train.shape[1],
    )

    train, test = apply_feature_engineering(train, test)

    pipeline_logger.log_step(
        step="Feature engineering — all transforms",
        rows_before=len(train) + len(test),
        rows_after=len(train) + len(test),
        cols_before=train.shape[1] - 2,  # days_to_license_expiry + license_expiry_missing added
        cols_after=train.shape[1],
        note="Risk encoded; dates parsed; license expiry engineered",
    )

    train_csv_name, test_csv_name = "risk_engineered_train.csv", "risk_engineered_test.csv"
    save_splits(train, train_csv_name, test, test_csv_name, stage)

    log_path = Path("logs/feature_engineering.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, test_csv_name