from __future__ import annotations


def render_gx(gx_results: dict) -> list[str]:
    """Return Markdown lines for the Great Expectations Suite section."""
    lines: list[str] = []
    a = lines.append

    a("---\n")
    a("## 3. Great Expectations Suite\n")

    status_icon = "PASSED" if gx_results["passed"] else "FAILED"
    a(f"**Overall Result: {status_icon}**\n")
    a("| Passed | Failed | Total |")
    a("|--------|--------|-------|")
    a(
        f"| {gx_results['pass_count']} "
        f"| {gx_results['fail_count']} "
        f"| {gx_results['pass_count'] + gx_results['fail_count']} |"
    )
    a("")

    a("### Expectation Results\n")
    a("| Status | Expectation | Column | Unexpected Count | Sample |")
    a("|--------|-------------|--------|-----------------|--------|")
    for r in gx_results["results"]:
        count = r["unexpected_count"] or "—"
        sample = ", ".join(str(s) for s in r["sample"]) if r["sample"] else "—"
        a(f"| `{r['type']}` | {r['column']} | {count} | {sample} |")
    a("")

    return lines
