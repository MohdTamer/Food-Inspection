from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import chart_layout, insight, section, subtitle
from science_the_data.dashboard.inject_css import SUBTEXT


def page_hotspots(pre_prune: Optional[dict]) -> None:
    st.title("📍 Failure Hotspots")
    subtitle(
        "Chicago is divided into geographic clusters based on the coordinates of every "
        "inspected establishment. Each dot represents one cluster; colour shows its failure "
        "rate and size shows how many inspections occurred there."
    )

    if pre_prune is None:
        st.warning("Location data not yet available — run the full pipeline to generate it.")
        return

    geo = pre_prune.get("geo_clusters")
    if not geo:
        st.warning("No geo cluster data found in cache.")
        return

    centers_df = pd.DataFrame(geo["cluster_centers"])
    sizes = [geo["cluster_sizes"].get(i, 1) for i in range(geo["n_clusters"])]

    c1, c2, c3 = st.columns(3)
    worst_cluster = max(geo["cluster_fail_rate"], key=geo["cluster_fail_rate"].get)
    c1.metric("Geographic Clusters", geo["n_clusters"])
    c2.metric("Highest-Risk Cluster Fail Rate", f"{geo['cluster_fail_rate'][worst_cluster]:.1%}")
    c3.metric("Missing Location Data", f"{geo['missing_pct'].get('Latitude', 0):.1%}")

    st.divider()

    col_map, col_bar = st.columns([3, 2])

    with col_map:
        section("Cluster Locations — Coloured by Fail Rate")
        fig_map = px.scatter(
            centers_df,
            x="Longitude",
            y="Latitude",
            color="fail_rate",
            size=sizes,
            size_max=40,
            color_continuous_scale="RdYlGn_r",
            hover_data={
                "cluster": True,
                "fail_rate": ":.1%",
                "Latitude": False,
                "Longitude": False,
            },
            labels={"fail_rate": "Fail Rate", "cluster": "Cluster"},
        )
        fig_map.update_coloraxes(
            colorbar_tickformat=".0%",
            colorbar_title=dict(text="Fail Rate"),
        )
        fig_map = chart_layout(fig_map)
        fig_map.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.19)", width=0.5)))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_bar:
        section("Fail Rate Ranking — All Clusters")
        fail_rate_df = pd.DataFrame(
            list(geo["cluster_fail_rate"].items()),
            columns=["Cluster", "Fail Rate"],
        ).sort_values("Fail Rate", ascending=True)
        fig_bar = px.bar(
            fail_rate_df,
            x="Fail Rate",
            y="Cluster",
            orientation="h",
            color="Fail Rate",
            color_continuous_scale="RdYlGn_r",
        )
        fig_bar.update_coloraxes(showscale=False)
        fig_bar.update_traces(hovertemplate="Cluster %{y}<br>Fail Rate: %{x:.1%}<extra></extra>")
        overall_mean = sum(geo["cluster_fail_rate"].values()) / len(geo["cluster_fail_rate"])
        fig_bar.add_vline(
            x=overall_mean,
            line_dash="dash",
            line_color="rgba(255,255,255,0.25)",
            annotation_text=f"City avg {overall_mean:.1%}",
            annotation_font_color=SUBTEXT,
        )
        fig_bar = chart_layout(fig_bar)
        fig_bar.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig_bar, use_container_width=True)

    insight(
        f"Cluster <strong>{worst_cluster}</strong> has the highest failure rate "
        f"(<strong>{geo['cluster_fail_rate'][worst_cluster]:.1%}</strong>), well above "
        f"the city average of <strong>{overall_mean:.1%}</strong>. "
        "Prioritising inspection resources in high-risk clusters could surface violations "
        "earlier."
    )
