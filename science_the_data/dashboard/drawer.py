import plotly.graph_objects as go
import streamlit as st

from science_the_data.dashboard.inject_css import CHART_FONT, SUBTEXT, TEXT


def chart_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply consistent dark theme to every Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=TEXT, family=CHART_FONT)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=CHART_FONT, color=SUBTEXT, size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT),
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color=SUBTEXT),
            title=dict(font=dict(color=SUBTEXT)),
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=SUBTEXT),
        title_font=dict(color=SUBTEXT),
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color=SUBTEXT),
        title_font=dict(color=SUBTEXT),
    )
    return fig


def insight(text: str) -> None:
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)


def subtitle(text: str) -> None:
    st.markdown(f'<p class="page-subtitle">{text}</p>', unsafe_allow_html=True)


def section(text: str) -> None:
    st.markdown(f'<p class="section-label">{text}</p>', unsafe_allow_html=True)
