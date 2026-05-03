from __future__ import annotations


def render_stats(stats: dict) -> list[str]:
    """Return Markdown lines for the Basic Statistics section."""
    lines: list[str] = []
    a = lines.append

    a("## 1. Basic Statistics\n")
    a("| Metric | Value |")
    a("|--------|-------|")
    a(f"| Rows | {stats['n_rows']:,} |")
    a(f"| Columns | {stats['n_cols']} |")
    a(f"| Fully duplicate rows | {stats['full_duplicates']:,} |")
    a(f"| Duplicate Inspection IDs | {stats['id_duplicates']:,} |")
    a("")

    a("### Column Data Types\n")
    a("| Column | Type |")
    a("|--------|------|")
    for col, dtype in stats["dtypes"].items():
        a(f"| {col} | `{dtype}` |")
    a("")

    a("### Missing Values\n")
    if not stats["missing"]:
        a("No missing values found.\n")
    else:
        a("| Column | Missing Count | Missing % |")
        a("|--------|---------------|-----------|")
        for col, info in sorted(stats["missing"].items(), key=lambda x: -x[1]["count"]):
            a(f"| {col} | {info['count']:,} | {info['pct']}% |")
        a("")

    return lines
