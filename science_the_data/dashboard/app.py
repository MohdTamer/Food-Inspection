"""
EDA Dashboard
Run with:  streamlit run science_the_data/dashboard/app.py
"""
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CACHE_PATH = Path("eda_cache/eda_payload.pkl")

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Inspection EDA",
    page_icon="🍽️",
    layout="wide",
)


@st.cache_data
def load_payload() -> dict:
    if not CACHE_PATH.exists():
        st.error(
            f"EDA cache not found at `{CACHE_PATH}`. "
            "Run the EDA pipeline first (`make run`)."
        )
        st.stop()
    with open(CACHE_PATH, "rb") as f:
        return pickle.load(f)


payload = load_payload()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("🍽️ Inspection EDA")
page = st.sidebar.radio(
    "Section",
    ["Overview", "Distributions", "Missingness", "Correlations", "Temporal", "Geo"],
)

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

if page == "Overview":
    st.title("Dataset Overview")

    num_df: pd.DataFrame = payload["numeric_summary"]
    balance: dict = payload["class_balance"]

    col1, col2, col3 = st.columns(3)
    total = sum(balance["counts"].values())
    col1.metric("Total inspections", f"{total:,}")
    col2.metric("Pass rate", f"{balance['pct'].get(0, 0):.1f}%")
    col3.metric("Fail rate", f"{balance['pct'].get(1, 0):.1f}%")

    st.subheader("Class Balance")
    fig = px.pie(
        values=list(balance["counts"].values()),
        names=["Pass" if k == 0 else "Fail" for k in balance["counts"].keys()],
        color_discrete_sequence=["#2ecc71", "#e74c3c"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Numeric Feature Summary")
    st.dataframe(num_df.style.format("{:.3f}"), use_container_width=True)

# ---------------------------------------------------------------------------
# Distributions
# ---------------------------------------------------------------------------

elif page == "Distributions":
    st.title("Feature Distributions")

    st.subheader("Top Facility Types")
    ft: pd.Series = payload["top_facility_types"]
    fig = px.bar(x=ft.index, y=ft.values, labels={"x": "Facility Type", "y": "Count"})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Level")
        risk: pd.Series = payload["risk_distribution"]
        fig = px.bar(
            x=[str(r) for r in risk.index], y=risk.values,
            labels={"x": "Risk", "y": "Count"},
            color_discrete_sequence=["#e67e22"],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Inspection Type")
        it: pd.Series = payload["inspection_type_distribution"]
        fig = px.bar(
            x=it.index, y=it.values,
            labels={"x": "Inspection Type", "y": "Count"},
            color_discrete_sequence=["#3498db"],
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Missingness
# ---------------------------------------------------------------------------

elif page == "Missingness":
    st.title("Missing Values")

    miss: pd.DataFrame = payload["missing_summary"]
    if miss.empty:
        st.success("No missing values in the training set.")
    else:
        fig = px.bar(
            miss.reset_index(),
            x="index", y="missing_pct",
            labels={"index": "Column", "missing_pct": "Missing (%)"},
            color="missing_pct",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(miss, use_container_width=True)

# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------

elif page == "Correlations":
    st.title("Correlations")

    st.subheader("Correlation with Target (Results)")
    tc: pd.Series = payload["target_correlation"]
    if not tc.empty:
        fig = px.bar(
            x=tc.index, y=tc.values,
            labels={"x": "Feature", "y": "Correlation"},
            color=tc.values,
            color_continuous_scale="RdBu",
            color_continuous_midpoint=0,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Correlation Matrix")
    corr: pd.DataFrame = payload["numeric_correlation"]
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0,
        aspect="auto",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Temporal
# ---------------------------------------------------------------------------

elif page == "Temporal":
    st.title("Temporal Trends")

    iot: pd.Series = payload["inspections_over_time"]
    if not iot.empty:
        st.subheader("Inspections Over Time")
        fig = px.line(
            x=iot.index.astype(str), y=iot.values,
            labels={"x": "Period", "y": "Inspections"},
        )
        st.plotly_chart(fig, use_container_width=True)

    frot: pd.Series = payload["fail_rate_over_time"]
    if not frot.empty:
        st.subheader("Fail Rate Over Time")
        fig = px.line(
            x=frot.index.astype(str), y=frot.values,
            labels={"x": "Period", "y": "Fail Rate"},
            color_discrete_sequence=["#e74c3c"],
        )
        fig.add_hline(y=frot.mean(), line_dash="dash", line_color="grey",
                      annotation_text=f"Mean {frot.mean():.2%}")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Geo
# ---------------------------------------------------------------------------

elif page == "Geo":
    st.title("Geographic Distribution")

    geo_df: pd.DataFrame = payload["geo_sample"]
    if not geo_df.empty:
        st.subheader("Inspection Map")
        map_df = geo_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
        st.map(map_df[["lat", "lon"]])

        st.subheader("Fail Rate by Community Area")
        community: pd.DataFrame = payload["fail_rate_by_community"]
        if not community.empty:
            fig = px.bar(
                community.head(20),
                x="COMMUNITY AREA NAME", y="fail_rate",
                color="fail_rate",
                color_continuous_scale="Reds",
                labels={"fail_rate": "Fail Rate", "COMMUNITY AREA NAME": "Community"},
            )
            fig.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(community, use_container_width=True)