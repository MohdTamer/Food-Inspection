"""
Run with: make dashboard or streamlit run science_the_data/dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path
import pickle

import pandas as pd
import plotly.express as px
import streamlit as st

CACHE_PATH = Path("eda_cache/eda_payload.pkl")

st.set_page_config(
    page_title="Chicago Inspection EDA",
    page_icon="🍽️",
    layout="wide",
)


@st.cache_data
def load_payload() -> dict:
    if not CACHE_PATH.exists():
        st.error(
            f"EDA cache not found at `{CACHE_PATH}`. Run the EDA pipeline first (`make run`)."
        )
        st.stop()
    with open(CACHE_PATH, "rb") as f:
        return pickle.load(f)


payload = load_payload()


def show_overview():
    st.title("📊 Dataset Overview")

    balance = payload["class_balance"]
    num_df = payload["numeric_summary"]

    total = sum(balance["counts"].values())
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Inspections", f"{total:,}")
    c2.metric("Pass Rate", f"{balance['pct'].get(0, 0):.1f}%")
    c3.metric("Fail Rate", f"{balance['pct'].get(1, 0):.1f}%", delta_color="inverse")

    st.divider()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("Class Balance")
        fig = px.pie(
            values=list(balance["counts"].values()),
            names=["Pass", "Fail"],
            hole=0.5,
            color=["Pass", "Fail"],
            color_discrete_map={"Pass": "#2ecc71", "Fail": "#e74c3c"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Feature Statistics")
        st.dataframe(num_df.style.background_gradient(cmap="YlGnBu"), use_container_width=True)


def show_distributions():
    st.title("Feature Distributions")

    tab1, tab2, tab3 = st.tabs(["Facility Types", "Risk Levels", "Inspection Types"])

    with tab1:
        ft = payload["top_facility_types"]
        fig = px.bar(ft, orientation="h", labels={"value": "Count", "index": "Facility"})
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        risk = payload["risk_distribution"]
        fig = px.bar(
            x=risk.index.astype(str), y=risk.values, color=risk.values, title="Count by Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        it = payload["inspection_type_distribution"]
        st.plotly_chart(
            px.treemap(names=it.index, parents=["All"] * len(it), values=it.values),
            use_container_width=True,
        )


def show_correlations():
    st.title("Correlation Analysis")

    st.subheader("Target Correlation (Results)")
    tc = payload["target_correlation"]
    if not tc.empty:
        fig = px.bar(tc, color=tc.values, color_continuous_scale="RdBu_r", range_color=[-1, 1])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Feature Heatmap")
    corr = payload["numeric_correlation"]
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")  # type: ignore
    st.plotly_chart(fig, use_container_width=True)


def show_missingness():
    st.title("Missing Data Summary")
    miss = payload["missing_summary"]
    if miss.empty:
        st.success("Data is clean! No missing values found.")
    else:
        st.warning(f"Found {len(miss)} columns with missing values.")
        st.table(miss)


def show_violations():
    st.title("Violation Analysis")

    violation_data = payload.get("violations")
    if not violation_data:
        st.warning("No violation data found in cache.")
        return

    # Top level metrics
    c1, c2 = st.columns(2)
    c1.metric("Avg Violations / Inspection", f"{violation_data['mean_violations']:.2f}")
    c2.metric("Max Violations Found", int(violation_data["max_violations"]))

    st.divider()

    # Violation Distribution Plot
    st.subheader("Distribution of Violation Counts")
    dist_df = pd.DataFrame(
        list(violation_data["distribution"].items()),
        columns=["Num Violations", "Inspection Count"],
    )

    fig = px.bar(
        dist_df,
        x="Num Violations",
        y="Inspection Count",
        color="Inspection Count",
        color_continuous_scale="Viridis",
        labels={"Num Violations": "Number of Violations", "Inspection Count": "Frequency"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"**Correlation with Failure:** The correlation between violation count and a 'Fail' result is **{violation_data['correlation_with_result']:.3f}**."
    )


PAGES = {
    "Dashboard Overview": show_overview,
    "Distributions": show_distributions,
    "Correlations": show_correlations,
    "Missing Values": show_missingness,
    "Violations": show_violations,
}


def main():
    st.sidebar.title("🍽️ Inspection EDA")
    st.sidebar.markdown("---")
    selection = st.sidebar.radio("Navigate to:", list(PAGES.keys()))

    # Execute the selected function
    PAGES[selection]()


if __name__ == "__main__":
    main()
