from typing import Callable, Optional

from pipelines.validations import validations_pipeline
from science_the_data.helpers.types import DataSplits, PipelineStage
from science_the_data.pipelines.transformations.binarize_targets import (
    transformations_pipeline as binarize_targets_pipeline,
)
from science_the_data.pipelines.transformations.encoding_features import encode_features_pipeline
from science_the_data.pipelines.transformations.feature_engineering import (
    feature_engineering_pipeline,
)
from science_the_data.pipelines.transformations.pruning import pruning_pipeline


def run_validations_on_csvs(splits: DataSplits, stage: PipelineStage, eda=None) -> None:
    for csv_name in splits.as_tuple():
        validations_pipeline(csv_name, stage, eda)


def transformations_pipeline(
    splits: DataSplits,
    eda=None,
    pre_prune_eda_hook: Optional[Callable[[DataSplits], None]] = None,
) -> DataSplits:
    stage = PipelineStage.PROCESSED

    run_validations_on_csvs(splits, stage, eda)

    train, val, test = binarize_targets_pipeline(*splits.as_tuple(), stage)
    splits = DataSplits(train, val, test)
    run_validations_on_csvs(splits, stage)

    train, val, test = feature_engineering_pipeline(*splits.as_tuple(), stage)
    splits = DataSplits(train, val, test)
    run_validations_on_csvs(splits, stage)

    if pre_prune_eda_hook is not None:
        pre_prune_eda_hook(splits)

    train, val, test = pruning_pipeline(*splits.as_tuple(), stage)
    splits = DataSplits(train, val, test)
    run_validations_on_csvs(splits, stage)

    train, val, test = encode_features_pipeline(*splits.as_tuple(), stage)
    splits = DataSplits(train, val, test)
    run_validations_on_csvs(splits, stage)

    return splits
