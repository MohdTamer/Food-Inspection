"""
report.py
---------
Render validation results to a Markdown file in the reports/ directory.
All three sections (stats, quality, GX) are written in one pass.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


# ── Public API ────────────────────────────────────────────────────────────────

def write_report(
    stats:      dict,
    issues:     list[dict],
    gx_results: dict,
    output_dir: Path,
    filename:   str | None = None,
) -> Path:
    """
    Write a Markdown validation report and return the path it was written to.

    Parameters
    ----------
    stats       : output of compute_basic_stats()
    issues      : output of run_quality_checks()
    gx_results  : output of run_gx_validation()
    output_dir  : directory to write the report into (created if missing)
    filename    : override the default timestamped name
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"validation_report_{ts}.md"
    path     = output_dir / filename

    lines: list[str] = []
    _append = lines.append

    # ── Header ────────────────────────────────────────────────────────────────
    _append(f"# Validation Report")
    _append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    _append("---\n")

    # ── Section 1: Basic Statistics ───────────────────────────────────────────
    _append("## 1. Basic Statistics\n")
    _append(f"| Metric | Value |")
    _append(f"|--------|-------|")
    _append(f"| Rows | {stats['n_rows']:,} |")
    _append(f"| Columns | {stats['n_cols']} |")
    _append(f"| Fully duplicate rows | {stats['full_duplicates']:,} |")
    _append(f"| Duplicate Inspection IDs | {stats['id_duplicates']:,} |")
    _append("")

    # Data types table
    _append("### Column Data Types\n")
    _append("| Column | Type |")
    _append("|--------|------|")
    for col, dtype in stats["dtypes"].items():
        _append(f"| {col} | `{dtype}` |")
    _append("")

    # Missing values
    _append("### Missing Values\n")
    if not stats["missing"]:
        _append("✅ No missing values found.\n")
    else:
        _append("| Column | Missing Count | Missing % |")
        _append("|--------|---------------|-----------|")
        for col, info in sorted(stats["missing"].items(), key=lambda x: -x[1]["count"]):
            _append(f"| {col} | {info['count']:,} | {info['pct']}% |")
        _append("")

    # ── Section 2: Quality Issues ─────────────────────────────────────────────
    _append("---\n")
    _append("## 2. Domain Quality Checks\n")

    if not issues:
        _append("✅ No quality issues detected.\n")
    else:
        _append(f"⚠️ **{len(issues)} issue(s) found.**\n")
        _append("| Field | Issue | Count | Sample |")
        _append("|-------|-------|-------|--------|")
        for issue in issues:
            sample = ", ".join(str(s) for s in issue["sample"]) if issue["sample"] else "—"
            _append(f"| {issue['field']} | {issue['message']} | {issue['count']:,} | {sample} |")
        _append("")

    # ── Section 3: Great Expectations ─────────────────────────────────────────
    _append("---\n")
    _append("## 3. Great Expectations Suite\n")

    status_icon = "✅ PASSED" if gx_results["passed"] else "❌ FAILED"
    _append(f"**Overall Result: {status_icon}**\n")
    _append(f"| Passed | Failed | Total |")
    _append(f"|--------|--------|-------|")
    _append(
        f"| {gx_results['pass_count']} "
        f"| {gx_results['fail_count']} "
        f"| {gx_results['pass_count'] + gx_results['fail_count']} |"
    )
    _append("")

    _append("### Expectation Results\n")
    _append("| Status | Expectation | Column | Unexpected Count | Sample |")
    _append("|--------|-------------|--------|-----------------|--------|")
    for r in gx_results["results"]:
        icon    = "✅" if r["passed"] else "❌"
        count   = r["unexpected_count"] or "—"
        sample  = ", ".join(str(s) for s in r["sample"]) if r["sample"] else "—"
        _append(f"| {icon} | `{r['type']}` | {r['column']} | {count} | {sample} |")
    _append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path