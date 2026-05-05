from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import chart_layout, insight, subtitle
from science_the_data.dashboard.inject_css import (
    ACCENT,
    FAIL_COLOR,
    PASS_COLOR,
    SUBTEXT,
)


def page_tenure(raw: Optional[dict]) -> None:
    st.title("📅 Business Age & Risk")
    subtitle(
        "Does the age of an establishment — measured as days from license issuance to "
        "inspection — affect its likelihood of failing? This page explores whether "
        "newer businesses carry higher risk."
    )

    if raw is None or "business_tenure" not in raw:
        st.info("Business age data not yet available — run the full pipeline first (`make run`).")
        return

    bt = raw["business_tenure"]
    desc = bt["describe"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Business Age at Inspection", f"{desc.get('mean', 0):,.0f} days")
    c2.metric("Median", f"{desc.get('50%', 0):,.0f} days")
    c3.metric("Records Missing Dates", f"{bt['missing']:,}")
    c4.metric("Removed (invalid negative dates)", f"{bt['negative_count']:,}")

    st.divider()

    by_class = bt.get("by_class", {})
    if by_class:
        rows = []
        for cls_key, counts in by_class.items():
            label = "Pass" if int(cls_key) == 0 else "Fail"
            for bucket, n in counts.items():
                rows.append({"Outcome": label, "Business Age": bucket, "Inspections": n})

        tenure_df = pd.DataFrame(rows)
        tenure_df["Outcome"] = tenure_df["Outcome"].astype(str)

        tenure_df["_sort_key"] = tenure_df["Business Age"].str.extract(r"(\d+)").astype(int)
        tenure_df = tenure_df.sort_values("_sort_key").drop(columns="_sort_key")

        fig = px.bar(
            tenure_df,
            x="Business Age",
            y="Inspections",
            color="Outcome",
            barmode="group",
            color_discrete_map={"Pass": PASS_COLOR, "Fail": FAIL_COLOR},
        )
        fig = chart_layout(fig, "Inspection Outcomes by Business Age Bracket")
        st.plotly_chart(fig, use_container_width=True)

        # Derived fail-rate per bucket
        pivot = tenure_df.pivot_table(
            index="Business Age", columns="Outcome", values="Inspections", aggfunc="sum"
        ).fillna(0)

        if "Pass" in pivot.columns and "Fail" in pivot.columns:
            pivot["Fail Rate"] = pivot["Fail"] / (pivot["Pass"] + pivot["Fail"])
            pivot = pivot.sort_index(
                key=lambda idx: idx.str.extract(r"(\d+)")[0].astype(int)
            ).reset_index()

            fig2 = px.line(
                pivot,
                x="Business Age",
                y="Fail Rate",
                markers=True,
                color_discrete_sequence=[ACCENT],
            )

            fig2.add_hline(
                y=pivot["Fail Rate"].mean(),
                line_dash="dash",
                line_color="rgba(255,255,255,0.25)",
                annotation_text="Average",
                annotation_font_color=SUBTEXT,
            )

            fig2.update_yaxes(tickformat=".0%")
            fig2 = chart_layout(fig2, "Fail Rate Across Business Age Brackets")
            st.plotly_chart(fig2, use_container_width=True)

        insight(
            "If fail rates are elevated in the earliest age brackets, this suggests a case "
            "for <strong>prioritising newly-licensed establishments</strong> in inspection "
            "scheduling — catching problems before they become entrenched."
        )

    else:
        st.info("Per-class tenure breakdown not available in this cache.")
