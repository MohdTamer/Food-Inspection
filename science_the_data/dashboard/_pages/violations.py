from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import subtitle, chart_layout, insight


def page_violations(final: dict, raw: Optional[dict]) -> None:
    st.title("⚠️ Violation Patterns")
    subtitle(
        "How many violations are typically found per inspection, and how strongly do "
        "violation counts predict a failure? Understanding this relationship helps "
        "calibrate how inspectors should weight individual findings."
    )

    vd = final.get("violations")

    if vd:
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Violations per Inspection", f"{vd['mean_violations']:.1f}")
        c2.metric("Maximum Found in One Inspection", int(vd["max_violations"]))
        corr = vd["correlation_with_result"]
        c3.metric(
            "Correlation with Failure",
            f"{corr:.3f}",
            help="Pearson correlation between violation count and a failed outcome (0–1 scale).",
        )
        st.divider()

    tab1, tab2 = st.tabs(["  📊  Post-Processing  ", "  🗂️  Raw (Pre-Processing)  "])

    with tab1:
        if not vd:
            st.warning("Final violation data not available.")
        else:
            dist_df = pd.DataFrame(
                list(vd["distribution"].items()),
                columns=["Violations Found", "No. of Inspections"],
            )
            fig = px.bar(
                dist_df,
                x="Violations Found",
                y="No. of Inspections",
                color="No. of Inspections",
                color_continuous_scale="Blues",
            )
            fig.update_coloraxes(showscale=False)
            fig = chart_layout(fig, "How Many Violations Does a Typical Inspection Find?")
            st.plotly_chart(fig, use_container_width=True)

            strength = "strong" if abs(corr) > 0.4 else "moderate" if abs(corr) > 0.2 else "weak" # type: ignore
            insight(
                f"There is a <strong>{strength} positive correlation ({corr:.3f})</strong> between " # type: ignore
                "the number of violations found and a failed outcome. "
                "In practice this means inspectors finding more violations should treat that "
                "as an escalating failure signal, not just a list of items to address."
            )

    with tab2:
        if raw is None or "raw_violations" not in raw:
            st.info(
                "Raw violation data not available — run the raw EDA pipeline first (`make run`)."
            )
        else:
            rv = raw["raw_violations"]
            raw_dist_df = pd.DataFrame(
                list(rv["distribution"].items()),
                columns=["Violations Found", "Frequency"],
            ).sort_values("Violations Found")

            describe = rv["describe"]
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Mean (raw)",   f"{describe.get('mean', 0):.1f}")
            rc2.metric("Median (raw)", f"{describe.get('50%', 0):.0f}")
            rc3.metric("Max (raw)",    f"{describe.get('max', 0):.0f}")

            fig_raw = px.bar(
                raw_dist_df,
                x="Violations Found",
                y="Frequency",
                color="Frequency",
                color_continuous_scale="Purples",
            )
            fig_raw.update_coloraxes(showscale=False)
            fig_raw = chart_layout(fig_raw, "Raw Violation Count Distribution (before cleaning)")
            st.plotly_chart(fig_raw, use_container_width=True)

            insight(
                "The raw distribution is wider and noisier than the post-processing view — "
                "evidence that the cleaning pipeline is removing erroneous outliers and "
                "normalising the violation text format."
            )