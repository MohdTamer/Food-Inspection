import streamlit as st

PASS_COLOR = "#27ae60"
FAIL_COLOR = "#e74c3c"
BLUE = "#2980b9"
DARK = "#1a1a2e"
MID = "#16213e"
CARD_BG = "#0f3460"
TEXT = "#e0e0e0"
SUBTEXT = "#a0a0b0"
ACCENT = "#e94560"
CHART_FONT = "IBM Plex Sans"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {{
            font-family: 'IBM Plex Sans', sans-serif;
            background-color: {DARK};
            color: {TEXT};
        }}

        /* Main container */
        .main .block-container {{
            padding: 2rem 2.5rem 3rem;
            max-width: 1400px;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {MID};
            border-right: 1px solid #ffffff12;
        }}
        section[data-testid="stSidebar"] .stRadio label {{
            font-size: 0.875rem;
            color: {SUBTEXT};
            padding: 0.35rem 0;
        }}
        section[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div {{
            color: {TEXT} !important;
            font-weight: 600;
        }}

        /* Metric cards */
        div[data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid #ffffff10;
            border-radius: 10px;
            padding: 1rem 1.25rem;
        }}
        div[data-testid="stMetric"] label {{
            font-size: 0.7rem !important;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {SUBTEXT} !important;
        }}
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
            font-size: 2rem !important;
            font-weight: 600 !important;
            color: {TEXT} !important;
        }}

        /* Page title */
        h1 {{
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            color: {TEXT} !important;
            margin-bottom: 0.25rem !important;
        }}

        /* Section subheaders */
        h2, h3 {{
            color: {TEXT} !important;
            font-weight: 500 !important;
        }}

        /* Divider */
        hr {{
            border-color: #ffffff12 !important;
            margin: 1.5rem 0 !important;
        }}

        /* Info / warning / success boxes */
        div[data-testid="stAlert"] {{
            background-color: {CARD_BG} !important;
            border: 1px solid #ffffff15 !important;
            border-radius: 8px;
        }}

        /* Tables */
        .stTable table {{
            background-color: {CARD_BG};
            border-radius: 8px;
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background-color: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {CARD_BG};
            border-radius: 6px 6px 0 0;
            color: {SUBTEXT};
            font-size: 0.8rem;
            letter-spacing: 0.04em;
            padding: 0.5rem 1rem;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {ACCENT} !important;
            color: #ffffff !important;
        }}

        /* Page subtitle helper */
        .page-subtitle {{
            font-size: 0.9rem;
            color: {SUBTEXT};
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }}

        /* Insight callout */
        .insight-box {{
            background: linear-gradient(135deg, {CARD_BG}cc, {MID}cc);
            border-left: 3px solid {ACCENT};
            border-radius: 0 8px 8px 0;
            padding: 0.85rem 1.1rem;
            margin: 1rem 0;
            font-size: 0.875rem;
            color: {TEXT};
            line-height: 1.6;
        }}
        .insight-box strong {{
            color: #ffffff;
        }}

        /* Section label */
        .section-label {{
            font-size: 0.65rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {SUBTEXT};
            margin-bottom: 0.5rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
