from pipelines.validations import validations_pipeline
from science_the_data.helpers.types import PipelineStage
from science_the_data.pipelines.cleaning.drop_columns import drop_useless_columns_pipeline
from science_the_data.pipelines.cleaning.drop_nulls import remove_nulls_dups_pipeline
from science_the_data.pipelines.cleaning.geo_features import geo_blocking_pipeline
from science_the_data.pipelines.cleaning.quarintine import quarantine_pipeline


def cleaning_pipeline(raw_csv_name: str) -> str:
    validations_pipeline(raw_csv_name, PipelineStage.RAW)

    stage = PipelineStage.INTERIM

    csv = remove_nulls_dups_pipeline(raw_csv_name, stage)
    validations_pipeline(csv, stage)

    csv = drop_useless_columns_pipeline(csv, stage)
    validations_pipeline(csv, stage)

    csv = geo_blocking_pipeline(csv, stage)
    validations_pipeline(csv, stage)

    stage = PipelineStage.CLEANED

    quarantined_csv = quarantine_pipeline(csv, stage)
    validations_pipeline(quarantined_csv, stage)

    clean_csv = "clean_final.csv"

    return clean_csv
