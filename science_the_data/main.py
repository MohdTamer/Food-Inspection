from pipelines.validations import validations_pipeline
from science_the_data.helpers.types import PipelineStage
from science_the_data.pipelines.drop_nulls import remove_nulls_dups_pipeline
from pipelines.geo_features import geo_blocking_pipeline
from pipelines.quarintine import quarantine_pipeline
from pipelines.drop_columns import drop_useless_columns_pipeline
from pipelines.split_data import splitting_pipeline
from pipelines.binarize_targets import transformations_pipeline
from pipelines.feature_engineering import feature_engineering_pipeline

import typer

app = typer.Typer()

@app.command()
def main():
    raw_csv_file_name = "merged_inspections_licenses_inner.csv"
    STAGE = PipelineStage.RAW
    validations_pipeline(raw_csv_file_name, STAGE)
    
    STAGE = PipelineStage.INTERIM

    outputFileName = remove_nulls_dups_pipeline(raw_csv_file_name, STAGE)
    validations_pipeline(outputFileName, STAGE)

    outputFileName = drop_useless_columns_pipeline(outputFileName, STAGE)
    validations_pipeline(outputFileName, STAGE)

    outputFileName = geo_blocking_pipeline(outputFileName, STAGE)
    validations_pipeline(outputFileName, STAGE)

    STAGE = PipelineStage.CLEANED
    quarntined = quarantine_pipeline(outputFileName, STAGE)
    validations_pipeline(quarntined, STAGE)
    quarntined = "clean_final.csv"

    train_csv, val_csv, test_csv, eda = splitting_pipeline(
        input_csv_name=quarntined,
        input_stage=PipelineStage.CLEANED,
        output_stage=PipelineStage.PROCESSED,
    )

    STAGE = PipelineStage.PROCESSED

    apply_validation_pipeline_to_list((train_csv, val_csv, test_csv), STAGE, eda)

    train_csv, val_csv, test_csv = transformations_pipeline(
        train_csv, val_csv, test_csv, PipelineStage.PROCESSED
    )
    apply_validation_pipeline_to_list((train_csv, val_csv, test_csv), STAGE)

    train_csv, val_csv, test_csv = feature_engineering_pipeline(
        train_csv, val_csv, test_csv, PipelineStage.PROCESSED
    )
    apply_validation_pipeline_to_list((train_csv, val_csv, test_csv), STAGE)

def apply_validation_pipeline_to_list(csv_names: tuple, stage: PipelineStage, eda = None) -> None:
    for item in csv_names:
        validations_pipeline(item, stage, eda)

if __name__ == "__main__":
    app()