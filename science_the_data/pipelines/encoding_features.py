from __future__ import annotations

from pathlib import Path

from loguru import logger

from helpers.pipeline_logger import PipelineLogger
from helpers.splits_io import load_splits, save_splits
from science_the_data.helpers.types import PipelineStage, SplitData
from science_the_data.transformations.categorical_encodings import encode_categorical_features
from science_the_data.transformations.inspection_history_encoding import add_inspection_history_features


def encode_features_pipeline(
    train_csv_name: str,
    val_csv_name: str,
    test_csv_name: str,
    input_stage: PipelineStage = PipelineStage.PROCESSED,
    output_stage: PipelineStage = PipelineStage.PROCESSED,
) -> tuple[str, str, str]:
    """Orchestrate temporal history features and categorical encodings.

    Step 1 — ``add_inspection_history_features``
        Combines all splits in chronological order to compute lag / rolling
        features without leakage, then re-splits.

    Step 2 — ``encode_categorical_features``
        Applies target encoding (inspection type, facility type), a binary
        revocation flag, ordinal application-type encoding, and finally drops
        the raw source columns that are no longer needed.

    Parameters
    ----------
    train_csv_name, val_csv_name, test_csv_name:
        Input CSV file names, resolved against *input_stage*.
    input_stage:
        Pipeline stage from which the CSVs are read.
    output_stage:
        Pipeline stage to which the encoded CSVs are written.

    Returns
    -------
    Tuple of (train, val, test) output file names.
    """
    pipeline_logger = PipelineLogger()

    train, val, test = load_splits(train_csv_name, val_csv_name, test_csv_name, input_stage)

    total_rows = len(train) + len(val) + len(test)
    pipeline_logger.log_step(
        step="Initial Load — encode features pipeline",
        rows_before=total_rows,
        rows_after=total_rows,
        cols_before=train.shape[1],
        cols_after=train.shape[1],
    )

    # --- step 1: temporal history features ---
    cols_before = train.shape[1]
    train, val, test = add_inspection_history_features(train, val, test)
    cols_after = train.shape[1]

    for label, subset in [("train", train), ("val", val), ("test", test)]:
        pipeline_logger.log_step(
            step=f"Inspection history features — {label}",
            rows_before=len(subset),
            rows_after=len(subset),
            cols_before=cols_before,
            cols_after=cols_after,
            note="Added: days_since_last_inspection, prev_inspection_result, fail_rate_last_3",
        )

    # --- step 2: categorical encodings + raw column drop ---
    cols_before = train.shape[1]
    train, val, test = encode_categorical_features(train, val, test)
    cols_after = train.shape[1]

    for label, subset in [("train", train), ("val", val), ("test", test)]:
        pipeline_logger.log_step(
            step=f"Categorical encodings — {label}",
            rows_before=len(subset),
            rows_after=len(subset),
            cols_before=cols_before,
            cols_after=cols_after,
            note=(
                "Added: inspection_type_encoded, facility_type_encoded, "
                "is_revoked, application_type_encoded; "
                "dropped raw source columns"
            ),
        )

    train_csv_name = "encoded_features_train.csv"
    val_csv_name   = "encoded_features_val.csv"
    test_csv_name  = "encoded_features_test.csv"

    train_csv_name, val_csv_name, test_csv_name = save_splits(
        train=SplitData(df=train, file_name=train_csv_name),
        val=SplitData(df=val,   file_name=val_csv_name),
        test=SplitData(df=test, file_name=test_csv_name),
        stage=output_stage,
    )

    log_path = Path("logs/encode_features.csv")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_logger.save(log_path)
    logger.info("Saved pipeline log → {}", log_path)

    return train_csv_name, val_csv_name, test_csv_name