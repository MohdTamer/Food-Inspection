from loguru import logger

from reports.model_report import write_model_report
from science_the_data.helpers.path_resolver import PathResolver
from science_the_data.helpers.types import DataSplits, PipelineStage
from science_the_data.pipelines.modeling.train_models import train_models_pipeline


def _report_filename(split: str) -> str:
    """'XGBoost — Val' -> 'model_report_xgboost.md'"""
    name = split.replace("—", "").replace("Val", "").strip().lower().replace(" ", "_")
    return f"model_report_{name}.md"


def modelling_pipeline(splits: DataSplits) -> None:
    results = train_models_pipeline(*splits.as_tuple(), PipelineStage.PROCESSED)

    report_dir = PathResolver.get_report_path_from_stage(splits.train, PipelineStage.PROCESSED)

    for result in results:
        filename = _report_filename(result["split"])
        logger.info("Writing {} ...", filename)
        report_path = write_model_report(
            results=[result],
            output_dir=report_dir,
            filename=filename,
        )
        logger.success("Model report saved → {}", report_path)
