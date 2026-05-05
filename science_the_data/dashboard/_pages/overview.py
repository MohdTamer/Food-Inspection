import plotly.express as px
import streamlit as st

from science_the_data.dashboard.drawer import chart_layout, insight, section, subtitle
from science_the_data.dashboard.inject_css import CHART_FONT, FAIL_COLOR, PASS_COLOR, TEXT


def page_overview(final: dict) -> None:
    st.title("🏙️ City Overview")
    subtitle(
        "A high-level picture of food safety across Chicago — how many establishments "
        "are inspected, how often they pass, and what the overall risk landscape looks like."
    )

    balance = final["class_balance"]
    total = sum(balance["counts"].values())
    pass_n = balance["counts"].get(0, 0)
    fail_n = balance["counts"].get(1, 0)
    fail_pct = balance["pct"].get(1, 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Inspections", f"{total:,}")
    c2.metric("Passed", f"{pass_n:,}")
    c3.metric("Failed", f"{fail_n:,}")
    c4.metric("City-wide Failure Rate", f"{fail_pct:.1f}%")

    st.divider()

    col_a, col_b = st.columns([1, 1])

    with col_a:
        section("Pass / Fail Split")
        fig = px.pie(
            values=[pass_n, fail_n],
            names=["Pass", "Fail"],
            hole=0.6,
            color_discrete_sequence=[PASS_COLOR, FAIL_COLOR],
        )
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        fig = chart_layout(fig)
        fig.add_annotation(
            text=f"{fail_pct:.1f}%<br><span style='font-size:11px'>Fail Rate</span>",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color=TEXT, family=CHART_FONT),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("Feature Statistics")
        num_df = final["numeric_summary"]
        st.dataframe(
            num_df.style.background_gradient(cmap="Blues", axis=0),
            use_container_width=True,
            height=340,
        )

    insight(
        f"<strong>{fail_pct:.1f}%</strong> of inspected establishments failed — roughly "
        f"<strong>1 in {round(100 / fail_pct)}</strong> inspections ends in a failure. "
        "Identifying which facility types and neighbourhoods drive this number is the focus "
        "of the pages that follow."
    )
