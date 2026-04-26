from science_the_data.helpers.path_resolver import PathResolver, Path
from pipelines.raw import raw_pipeline
from pipelines.remove_nulls_dups import remove_nulls_dups
import typer

REPORTS_DIR = Path("reports")

app = typer.Typer()

@app.command()
def main():
    raw_pipeline()
    remove_nulls_dups()

if __name__ == "__main__":
    app()