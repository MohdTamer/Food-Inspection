from __future__ import annotations

from validations.types import Issue


def render_quality(issues: list[Issue]) -> list[str]:
    """Return Markdown lines for the Domain Quality Checks section."""
    lines: list[str] = []
    a = lines.append

    a("---\n")
    a("## 2. Domain Quality Checks\n")

    if not issues:
        a("No quality issues detected.\n")
    else:
        a(f"**{len(issues)} issue(s) found.**\n")
        a("| Field | Issue | Count | Sample |")
        a("|-------|-------|-------|--------|")
        for issue in issues:
            sample = ", ".join(str(s) for s in issue["sample"]) if issue["sample"] else "—"
            a(f"| {issue['field']} | {issue['message']} | {issue['count']:,} | {sample} |")
        a("")

    return lines
