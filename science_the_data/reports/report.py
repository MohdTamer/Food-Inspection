"""
reports/report.py
-----------------
Orchestrates section renderers and writes the final Markdown report.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from validations.types import Issue
from reports.sections.gx import render_gx
from reports.sections.quality import render_quality
from reports.sections.stats import render_stats


def _build_header() -> list[str]:
    lines = []
    lines.append("# Validation Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")
    return lines


def write_report(
    stats: dict,
    issues: list[Issue],
    gx_results: dict,
    output_dir: Path,
    skip_gx: bool = False,
    filename: str | None = None,
) -> Path:
    """
    Write a Markdown validation report and return the path it was written to.

    Parameters
    ----------
    stats      : output of compute_basic_stats()
    issues     : output of run_quality_checks()
    gx_results : output of run_gx_validation()
    output_dir : directory to write the report into (created if missing)
    skip_gx    : when True, the Great Expectations section is omitted
    filename   : override the default timestamped name
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"validation_report_{ts}.md"
    path = output_dir / filename

    sections = [
        _build_header(),
        render_stats(stats),
        render_quality(issues),
        *([] if skip_gx else [render_gx(gx_results)]),
    ]

    content = "\n".join(line for section in sections for line in section)
    path.write_text(content, encoding="utf-8")
    return path