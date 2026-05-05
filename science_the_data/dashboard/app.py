"""
Chicago Food Inspection Dashboard
Run with: make dashboard  OR  streamlit run science_the_data/dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path
import pickle
from typing import Optional

import streamlit as st

from science_the_data.dashboard._pages.drivers import page_drivers
from science_the_data.dashboard._pages.facilities import page_facilities
from science_the_data.dashboard._pages.hotspots import page_hotspots
from science_the_data.dashboard._pages.overview import page_overview
from science_the_data.dashboard._pages.tenure import page_tenure
from science_the_data.dashboard._pages.violations import page_violations
from science_the_data.dashboard.inject_css import inject_css
from science_the_data.helpers.path_resolver import PathResolver

CACHE_PATHS = {
    "raw": PathResolver.get_eda_cache_dir("eda_raw_payload.pkl"),
    "pre_prune": PathResolver.get_eda_cache_dir("eda_pre_prune_payload.pkl"),
    "final": PathResolver.get_eda_cache_dir("eda_payload.pkl"),
}

st.set_page_config(
    page_title="Chicago Food Inspections",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_payload(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


PAGES = {
    "🏙️  City Overview": "overview",
    "📍  Failure Hotspots": "hotspots",
    "🏢  Facility Insights": "facilities",
    "⚠️  Violation Patterns": "violations",
    "📅  Business Age & Risk": "tenure",
    "🔑  Key Risk Drivers": "drivers",
}

REQUIRES = {
    "overview": ["final"],
    "hotspots": ["pre_prune"],
    "facilities": ["final"],
    "violations": ["final"],  # raw is optional / shown in tab
    "tenure": ["raw"],
    "drivers": ["final"],
    "quality": ["final"],
}


def main() -> None:
    inject_css()

    raw = load_payload(CACHE_PATHS["raw"])
    pre_prune = load_payload(CACHE_PATHS["pre_prune"])
    final = load_payload(CACHE_PATHS["final"])

    st.sidebar.title("Chicago Food\nInspections")
    st.sidebar.markdown("---")

    selection = st.sidebar.radio("", list(PAGES.keys()), label_visibility="collapsed")
    page_key = PAGES[selection]

    # Guard: check required caches
    required = REQUIRES[page_key]
    caches = {"raw": raw, "pre_prune": pre_prune, "final": final}
    missing_caches = [k for k in required if caches[k] is None]

    if missing_caches and page_key not in ("violations", "tenure"):
        cache_names = {"raw": "raw EDA", "pre_prune": "pre-prune EDA", "final": "final EDA"}
        names = ", ".join(cache_names[k] for k in missing_caches)
        st.warning(f"This page requires the **{names}** cache. Run `make run` to generate it.")
        return

    if page_key == "overview":
        page_overview(final)  # type: ignore
    elif page_key == "hotspots":
        page_hotspots(pre_prune)
    elif page_key == "facilities":
        page_facilities(pre_prune)
    elif page_key == "violations":
        page_violations(final, raw)  # type: ignore
    elif page_key == "tenure":
        page_tenure(raw)
    elif page_key == "drivers":
        page_drivers(final)  # type: ignore

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p style="font-size:0.7rem; color:#555; line-height:1.6">'
        "Data: City of Chicago Data Portal<br>"
        "Model performance metrics are in the separate model dashboard."
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
