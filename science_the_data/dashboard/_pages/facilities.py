from __future__ import annotations

from typing import Optional

import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import subtitle, section, chart_layout, insight
from science_the_data.dashboard.inject_css import BLUE, CARD_BG, TEXT


def page_facilities(pre_prune: Optional[dict]) -> None:
    st.title("🏢 Facility Insights")
    subtitle(
        "Which types of establishments are inspected most often, and how does the assigned "
        "risk level map onto actual failure rates? Use these views to understand where "
        "inspection effort is currently concentrated."
    )

    tab1, tab2 = st.tabs(
        ["  🏪  Failure Rate by Type  ", "  ⚠️  Risk vs Outcome  "]
    )

    with tab1:
        if pre_prune and "facility_fail_rates" in pre_prune:
            fr_df = pre_prune["facility_fail_rates"]

            col_a, col_b = st.columns([3, 2])

            with col_a:
                section("Fail Rate by Facility Type (min 50 inspections)")
                fig = px.bar(
                    fr_df.head(20),
                    x="fail_rate",
                    y="Facility Type",
                    orientation="h",
                    color="fail_rate",
                    color_continuous_scale="RdYlGn_r",
                    hover_data={"total": True, "failures": True},
                )
                fig.update_coloraxes(showscale=False)
                fig.update_xaxes(tickformat=".0%")
                fig = chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                section("Inspection Volume")
                vol_df = fr_df.sort_values("total", ascending=True).head(20)
                fig2 = px.bar(
                    vol_df,
                    x="total",
                    y="Facility Type",
                    orientation="h",
                    color="total",
                    color_continuous_scale=[[0, CARD_BG], [1, BLUE]],
                )
                fig2.update_coloraxes(showscale=False)
                fig2 = chart_layout(fig2)
                st.plotly_chart(fig2, use_container_width=True)

            worst = fr_df.iloc[0]
            insight(
                f"<strong>{worst['Facility Type']}</strong> has the highest failure rate "
                f"(<strong>{worst['fail_rate']:.1%}</strong>) across "
                f"<strong>{worst['total']:,}</strong> inspections. "
                "High volume + high fail rate is where inspection resources have the most leverage."
            )
        else:
            st.warning("Re-run the pipeline to generate pre-encode facility stats.")

    with tab2:
        if pre_prune and "risk_vs_outcome" in pre_prune:
            rv_df = pre_prune["risk_vs_outcome"]
            fig = px.bar(
                rv_df,
                x="Risk",
                y="fail_rate",
                color="fail_rate",
                color_continuous_scale="RdYlGn_r",
                text=rv_df["fail_rate"].map("{:.1%}".format),
                hover_data={"total": True},
            )
            fig.update_traces(textposition="outside", textfont_color=TEXT)
            fig.update_coloraxes(showscale=False)
            fig.update_yaxes(tickformat=".0%")
            fig = chart_layout(fig, "Assigned Risk Level vs Actual Failure Rate")
            st.plotly_chart(fig, use_container_width=True)

            insight(
                "If lower-risk categories have unexpectedly high failure rates, "
                "the administrative risk assignment is miscalibrated — "
                "a signal worth surfacing to inspection planners."
            )
        else:
            st.warning("Re-run the pipeline to generate risk vs outcome data.")