from helpers.path_resolver import Path, PathResolver
from validate import run_validations

def raw_pipeline():
    raw_csv_path = PathResolver.raw("merged_inspections_licenses_inner.csv")
    raw_report_path = Path("reports/markdown/raw")

    run_validations(raw_csv_path, raw_report_path, True)

