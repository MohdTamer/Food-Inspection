from pathlib import Path

from loguru import logger
import pandas as pd
import typer

from reports.sections.eda import render_eda
from science_the_data.helpers.path_resolver import PathResolver
from science_the_data.helpers.types import PipelineStage
from science_the_data.reports.validations_report import write_report
from science_the_data.validations.expectations import run_gx_validation
from science_the_data.validations.quality import run_quality_checks
from science_the_data.validations.stats import compute_basic_stats


def validations_pipeline(
    input_csv_name: str,
    stage: PipelineStage,
    eda: dict | None = None,
) -> None:
    csv_path = PathResolver.get_data_path_from_stage(input_csv_name, stage)
    report_dir = PathResolver.get_report_path_from_stage(input_csv_name, stage)
    extra_sections = [render_eda(eda, report_dir)] if eda else None
    run_validations(
        input_path=csv_path,
        output_dir=report_dir,
        skip_gx=True,
        extra_sections=extra_sections,
    )


def run_validations(
    input_path: Path = PathResolver.get_processed_data_path("output.csv"),
    output_dir: Path = PathResolver.REPORT_DIR,
    skip_gx: bool = typer.Option(False, "--skip-gx"),
    extra_sections: list[list[str]] | None = None,  # usually for EDAs
) -> None:
    logger.info("Running validations on {}", input_path)

    _cols = pd.read_csv(input_path, nrows=0).columns.tolist()
    _parse_dates = ["Inspection Date"] if "Inspection Date" in _cols else []
    df = pd.read_csv(input_path, parse_dates=_parse_dates)

    logger.info("Loaded {:,} rows × {} columns.", len(df), df.shape[1])

    logger.info("Computing basic statistics …")
    stats = compute_basic_stats(df)
    logger.info(
        "Stats: {:,} rows | {} columns with missing values | {} full duplicates",
        stats["n_rows"],
        len(stats["missing"]),
        stats["full_duplicates"],
    )

    logger.info("Running domain quality checks …")
    issues = run_quality_checks(df)

    if issues:
        logger.warning("{} quality issue(s) found:", len(issues))
        for issue in issues:
            logger.warning(
                "  [{}] {} — {:,} affected", issue["field"], issue["message"], issue["count"]
            )
    else:
        logger.info("No quality issues found.")

    gx_results: dict = {"passed": None, "pass_count": 0, "fail_count": 0, "results": []}

    if not skip_gx:
        logger.info("Running Great Expectations suite …")
        gx_results = run_gx_validation(df)
        level = "success" if gx_results["passed"] else "error"
        getattr(logger, level)(
            "GX suite {} — {} passed, {} failed.",
            "PASSED" if gx_results["passed"] else "FAILED",
            gx_results["pass_count"],
            gx_results["fail_count"],
        )
    else:
        logger.info("Skipping Great Expectations (--skip-gx).")

    logger.info("Writing report to {} …", output_dir)
    report_path = write_report(
        stats=stats,
        issues=issues,
        gx_results=gx_results,
        output_dir=output_dir,
        skip_gx=skip_gx,
        extra_sections=extra_sections,
    )
    logger.success("Validation report saved → {}", report_path)

    if gx_results["passed"] is False:
        raise typer.Exit(code=1)

    logger.info("Validations done.")
