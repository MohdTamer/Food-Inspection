import typer

from pipelines.split_data import splitting_pipeline
from science_the_data.helpers.types import DataSplits, PipelineStage
from science_the_data.pipelines.cleaning.cleaning_pipeline import cleaning_pipeline
from science_the_data.pipelines.transformations.transformations_pipeline import (
    transformations_pipeline,
)

app = typer.Typer()


def run_cleaning(raw_csv_name: str) -> str:
    return cleaning_pipeline(raw_csv_name)


def run_splitting(clean_csv_name: str) -> tuple[DataSplits, object]:
    train_csv, val_csv, test_csv, eda = splitting_pipeline(
        input_csv_name=clean_csv_name,
        input_stage=PipelineStage.CLEANED,
        output_stage=PipelineStage.PROCESSED,
    )
    return DataSplits(train_csv, val_csv, test_csv), eda

    train_models_pipeline(train_csv, val_csv, test_csv, PipelineStage.PROCESSED)

def run_transformations(splits: DataSplits, eda=None) -> DataSplits:
    return transformations_pipeline(splits, eda)


def run_modelling(splits: DataSplits) -> None:
    raise NotImplementedError("Modelling pipeline not yet implemented.")


@app.command()
def main() -> None:
    raw_csv_name = "merged_inspections_licenses_inner.csv"

    clean_csv = run_cleaning(raw_csv_name)
    splits, eda = run_splitting(clean_csv)
    splits = run_transformations(splits, eda)
    # run_modelling(splits)  # uncomment when ready


if __name__ == "__main__":
    app()