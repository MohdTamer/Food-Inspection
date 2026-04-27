from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from science_the_data.helpers.path_resolver     import PathResolver
from science_the_data.validations.stats         import compute_basic_stats
from science_the_data.validations.quality       import run_quality_checks
from science_the_data.validations.expectations  import run_gx_validation
from science_the_data.validations.report        import write_report

app = typer.Typer()

@app.command()
def run_validations(
    input_path: Path = PathResolver.get_processed_data_path("output.csv"),
    output_dir: Path = PathResolver.REPORT_DIR,
    skip_gx:    bool = typer.Option(False, "--skip-gx", help="Skip Great Expectations (faster)"),
):

    logger.info("running validations")
    logger.info(f"Loading data from {input_path} ...")
    df = pd.read_csv(input_path, parse_dates=["Inspection Date"])
    logger.info(f"Loaded {len(df):,} rows × {df.shape[1]} columns.")

    logger.info("Computing basic statistics ...")
    stats = compute_basic_stats(df)
    logger.info(
        f"Stats: {stats['n_rows']:,} rows | "
        f"{len(stats['missing'])} columns with missing values | "
        f"{stats['full_duplicates']} full duplicates"
    )

    logger.info("Running domain quality checks ...")
    issues = run_quality_checks(df)

    if issues:
        logger.warning(f"{len(issues)} quality issue(s) found:")
        for issue in issues:
            logger.warning(f"  [{issue['field']}] {issue['message']} — {issue['count']:,} affected")
    else:
        logger.info("No quality issues found.")

    gx_results: dict = {"passed": None, "pass_count": 0, "fail_count": 0, "results": []}

    if not skip_gx:
        logger.info("Running Great Expectations suite ...")
        gx_results = run_gx_validation(df)
        level = "success" if gx_results["passed"] else "error"
        getattr(logger, level)(
            f"GX suite {'PASSED' if gx_results['passed'] else 'FAILED'} — "
            f"{gx_results['pass_count']} passed, {gx_results['fail_count']} failed."
        )
    else:
        logger.info("Skipping Great Expectations (--skip-gx flag set).")

    logger.info(f"Writing report to {output_dir}/ ...")
    report_path = write_report(
        stats=stats,
        issues=issues,
        gx_results=gx_results,
        output_dir=output_dir,
    )
    logger.success(f"Validation report saved → {report_path}")

    if gx_results["passed"] is False:
        raise typer.Exit(code=1)
    
    logger.info("Validations done.")


if __name__ == "__main__":
    app()