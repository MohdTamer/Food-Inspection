from __future__ import annotations

import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import subtitle, section, chart_layout, insight
from science_the_data.dashboard.inject_css import FAIL_COLOR, PASS_COLOR, SUBTEXT


def page_drivers(final: dict) -> None:
    st.title("🔑 Key Risk Drivers")
    subtitle(
        "Which measurable characteristics of an establishment are most associated with "
        "failure? The charts below rank every available data point by how strongly it "
        "correlates with a failed inspection outcome."
    )

    tc = final["target_correlation"]
    if not tc.empty:
        tc_df = tc.reset_index()
        tc_df.columns = ["Feature", "Correlation with Failure"]
        tc_df = tc_df.sort_values("Correlation with Failure")

        pos_df = tc_df[tc_df["Correlation with Failure"] > 0]
        neg_df = tc_df[tc_df["Correlation with Failure"] <= 0]

        col_a, col_b = st.columns(2)

        with col_a:
            section("Increases Failure Risk ↑")
            fig_pos = px.bar(
                pos_df.tail(10),
                x="Correlation with Failure",
                y="Feature",
                orientation="h",
                color="Correlation with Failure",
                color_continuous_scale=[[0, "#f39c12"], [1, FAIL_COLOR]],
            )
            fig_pos.update_coloraxes(showscale=False)
            fig_pos = chart_layout(fig_pos)
            st.plotly_chart(fig_pos, use_container_width=True)

        with col_b:
            section("Associated with Passing ↓")
            fig_neg = px.bar(
                neg_df.head(10),
                x="Correlation with Failure",
                y="Feature",
                orientation="h",
                color="Correlation with Failure",
                color_continuous_scale=[[0, PASS_COLOR], [1, "#a8e6cf"]],
            )
            fig_neg.update_coloraxes(showscale=False)
            fig_neg = chart_layout(fig_neg)
            st.plotly_chart(fig_neg, use_container_width=True)

        st.divider()
        section("Full Feature Correlation Heatmap")

        corr = final["numeric_correlation"]
        fig_heat = px.imshow(
            corr,
            text_auto=".2f", # type: ignore
            color_continuous_scale="RdBu_r",
            aspect="auto",
            zmin=-1,
            zmax=1,
        )
        fig_heat.update_traces(textfont=dict(size=9, color="rgba(255,255,255,0.67)"))
        fig_heat = chart_layout(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

        top_driver = tc.index[0]
        top_val    = tc.iloc[0]
        direction  = "increases" if top_val > 0 else "reduces"
        insight(
            f"<strong>{top_driver}</strong> is the single strongest signal: "
            f"a higher value {direction} failure probability "
            f"(correlation = <strong>{top_val:.3f}</strong>). "
            "Inspectors and policy-makers should pay close attention to this "
            "feature when assessing establishments."
        )