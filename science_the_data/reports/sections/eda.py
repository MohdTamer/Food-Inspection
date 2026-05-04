"""
reports/sections/eda.py
------------------------
Renders the EDA section of a Markdown report.

``render_eda(eda, report_dir)`` accepts the dict produced by
``compute_eda_stats()`` and the directory where the report will be written.
It resolves each absolute figure path to a relative POSIX path so Markdown
renderers can find the images regardless of where the project root sits.

Expected *eda* keys (all optional — missing keys are silently skipped)
-----------------------------------------------------------------------
split_summary   : list[dict]  keys: split, rows, pct, date_start, date_end
date_range      : dict        keys: min, max, total_days
cutoff_date     : str
target_dist     : dict[split_label -> dict[class_label -> {count, pct}]]
class_labels    : list[str]
figures         : dict[figure_key -> absolute Path]
                  Recognised keys:
                    "target_distribution"   — bar chart per split
                    "inspections_over_time" — monthly volume line chart
"""

from __future__ import annotations

import os
from pathlib import Path

_FIGURE_CAPTIONS: dict[str, str] = {
    "target_distribution": "Target (`Results`) distribution across Train, Test, and Overall splits.",
    "inspections_over_time": "Monthly inspection volume coloured by split boundary.",
}


def render_eda(eda: dict, report_dir: Path) -> list[str]:
    """
    Return Markdown lines for the EDA section.

    Parameters
    ----------
    eda         : dict from ``compute_eda_stats()``
    report_dir  : directory the report will be written into — used to
                  compute relative paths to figures
    """
    lines: list[str] = []
    a = lines.append

    a("## 3. Exploratory Split Analysis\n")

    # ── Split summary ──────────────────────────────────────────────────────
    if "split_summary" in eda:
        a("### Split Summary\n")
        a("| Split | Rows | % of Total | Date Start | Date End |")
        a("|-------|-----:|------------|------------|----------|")
        for row in eda["split_summary"]:
            a(
                f"| {row['split']} "
                f"| {row['rows']:,} "
                f"| {row['pct']} "
                f"| {row['date_start']} "
                f"| {row['date_end']} |"
            )
        a("")

    # ── Date range ─────────────────────────────────────────────────────────
    if "date_range" in eda:
        dr = eda["date_range"]
        a("### Date Range\n")
        a("| Metric | Value |")
        a("|--------|-------|")
        a(f"| Earliest inspection   | {dr['min']} |")
        a(f"| Latest inspection     | {dr['max']} |")
        a(f"| Total days spanned    | {dr.get('total_days', 'N/A')} |")
        if "cutoff_date" in eda:
            a(f"| Temporal split cutoff | **{eda['cutoff_date']}** |")
        a("")

    # ── Target distribution table ──────────────────────────────────────────
    if "target_dist" in eda:
        a("### Target (`Results`) Distribution by Split\n")

        class_labels: list[str] = eda.get("class_labels") or sorted(
            {lbl for split_data in eda["target_dist"].values() for lbl in split_data}
        )
        split_names = list(eda["target_dist"].keys())

        a("| Class | " + " | ".join(f"{s} n | {s} %" for s in split_names) + " |")
        a("|-------|" + "------:|------:|" * len(split_names))

        for cls in class_labels:
            cells = [f"**{cls}**"]
            for split_data in eda["target_dist"].values():
                info = split_data.get(cls, {"count": 0, "pct": 0.0})
                cells.append(f"{info['count']:,}")
                cells.append(f"{info['pct']:.1f}%")
            a("| " + " | ".join(cells) + " |")

        a("")
        a(
            "> Large skew between Train and Test distributions may indicate "
            "concept drift across the time boundary.\n"
        )

    # ── Figures ────────────────────────────────────────────────────────────
    figures: dict[str, Path] = eda.get("figures", {})

    if figures:
        a("### Figures\n")

        for key, caption in _FIGURE_CAPTIONS.items():
            if key not in figures:
                continue
            rel = _rel(figures[key], report_dir)
            alt = caption.replace("`", "")
            a(f"![{alt}]({rel})\n")
            a(f"*{caption}*\n")

        # Any figure not in the known list (forward-compat)
        for key, abs_path in figures.items():
            if key in _FIGURE_CAPTIONS:
                continue
            rel = _rel(abs_path, report_dir)
            a(f"![{key}]({rel})\n")

    return lines


def _rel(abs_fig_path: Path, report_dir: Path) -> str:
    """POSIX relative path from *report_dir* to *abs_fig_path*."""
    return Path(os.path.relpath(abs_fig_path, report_dir)).as_posix()
