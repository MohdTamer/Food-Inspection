from loguru import logger
import typer

from science_the_data.helpers.types import DataSplits
from science_the_data.pipelines.modeling.modelling_pipeline import modelling_pipeline

app = typer.Typer()

_DEFAULT_SPLITS = DataSplits(
    train="encoded_features_train.csv",
    val="encoded_features_val.csv",
    test="encoded_features_test.csv",
)


@app.command()
def main(
    train_csv: str = _DEFAULT_SPLITS.train,
    val_csv: str = _DEFAULT_SPLITS.val,
    test_csv: str = _DEFAULT_SPLITS.test,
) -> None:
    splits = DataSplits(train=train_csv, val=val_csv, test=test_csv)
    logger.info("Starting modelling pipeline with splits: {}", splits)
    modelling_pipeline(splits)
    logger.success("Modelling complete.")


if __name__ == "__main__":
    app()
