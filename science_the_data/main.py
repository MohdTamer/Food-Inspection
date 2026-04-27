from pipelines.validations import validations_pipeline
from science_the_data.pipelines.types import PipelineStage
from pipelines.remove_nulls_dups import remove_nulls_dups_pipeline
import typer

app = typer.Typer()

@app.command()
def main():
    raw_csv_file_name = "merged_inspections_licenses_inner.csv"
    STAGE = PipelineStage.RAW
    validations_pipeline(raw_csv_file_name, STAGE)
    
    STAGE = PipelineStage.INTERIM
    outputFileName = remove_nulls_dups_pipeline(raw_csv_file_name, STAGE)

    STAGE = PipelineStage.INTERIM
    validations_pipeline(outputFileName, STAGE)

    


if __name__ == "__main__":
    app()