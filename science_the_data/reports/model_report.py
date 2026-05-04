from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reports.sections.models import render_models


def _build_header(title: str = "Model Training Report") -> list[str]:
    lines = []
    lines.append(f"# {title}")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")
    return lines


def write_model_report(
    results: list[dict],
    output_dir: Path,
    filename: str | None = None,
    extra_sections: list[list[str]] | None = None,
) -> Path:
    """
    Write a Markdown model-training report and return the path it was written to.

    Parameters
    ----------
    results         : list of per-model result dicts (see render_models for schema)
    output_dir      : directory to write the report into (created if missing)
    filename        : override the default timestamped name
    extra_sections  : optional list of pre-rendered section blocks appended after
                      the core model section (e.g. SHAP plots, confusion matrices)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"model_report_{ts}.md"
    path = output_dir / filename

    sections: list[list[str]] = [
        _build_header(),
        render_models(results),
    ]

    if extra_sections:
        sections.extend(extra_sections)

    content = "\n".join(line for section in sections for line in section)
    path.write_text(content, encoding="utf-8")
    return path
