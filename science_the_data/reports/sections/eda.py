from __future__ import annotations

import os
from pathlib import Path

_FIGURE_CAPTIONS: dict[str, str] = {
    "target_distribution": "Target (`Results`) distribution across Train, Test, and Overall splits.",
    "inspections_over_time": "Monthly inspection volume coloured by split boundary.",
}


def render_eda(eda: dict, report_dir: Path) -> list[str]:
    lines: list[str] = []
    a = lines.append

    a("## 3. Exploratory Split Analysis\n")

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

        for key, abs_path in figures.items():
            if key in _FIGURE_CAPTIONS:
                continue
            rel = _rel(abs_path, report_dir)
            a(f"![{key}]({rel})\n")

    return lines


def _rel(abs_fig_path: Path, report_dir: Path) -> str:
    """POSIX relative path from *report_dir* to *abs_fig_path*."""
    return Path(os.path.relpath(abs_fig_path, report_dir)).as_posix()
