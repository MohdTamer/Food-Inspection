import typer

from pipelines.split_data import splitting_pipeline
from science_the_data.helpers.types import DataSplits, PipelineStage
from science_the_data.pipelines.eda import (
    eda_final_pipeline,
    eda_pre_prune_pipeline,
    eda_raw_pipeline,
)

# from science_the_data.pipelines.eda.eda_final_pipeline import eda_final_pipeline
# from science_the_data.pipelines.eda.eda_pre_prune_pipeline import eda_pre_prune_pipeline
from science_the_data.pipelines.transformations.transformations_pipeline import (
    transformations_pipeline,
)

app = typer.Typer()


def run_splitting(clean_csv_name: str) -> tuple[DataSplits, object]:
    train_csv, val_csv, test_csv, eda = splitting_pipeline(
        input_csv_name=clean_csv_name,
        input_stage=PipelineStage.CLEANED,
        output_stage=PipelineStage.PROCESSED,
    )
    return DataSplits(train_csv, val_csv, test_csv), eda


@app.command()
def main() -> None:
    # PathResolver.ensureDirs()
    raw_csv_name = "merged_inspections_licenses_inner.csv"
    eda_raw_pipeline.eda_raw_pipeline(raw_csv_name)

    # clean_csv = cleaning_pipeline(raw_csv_name)
    # clean_csv = "clean_final.csv"

    # splits, eda = run_splitting(clean_csv)
    splits, eda = (
        DataSplits(
            "split_train.csv",
            "split_validation.csv",
            "split_test.csv",
        ),
        None,
    )

    splits = transformations_pipeline(splits, eda, eda_pre_prune_pipeline.eda_pre_prune_pipeline)
    splits = DataSplits(
        "encoded_features_train.csv", "encoded_features_val.csv", "encoded_features_test.csv"
    )

    eda_final_pipeline.eda_final_pipeline(splits)
    # modelling_pipeline(splits)


if __name__ == "__main__":
    app()
