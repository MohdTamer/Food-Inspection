from helpers.path_resolver import PathResolver
from validate import run_validations
from science_the_data.pipelines.types import PipelineStage

def validations_pipeline(input_csv_name: str, stage: PipelineStage):
    csv_path = PathResolver.get_data_path_from_stage(input_csv_name, stage)
    report_path = PathResolver.get_report_path_from_stage(input_csv_name, stage)
    run_validations(csv_path, report_path, True)

