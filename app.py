"""
app.py  —  KNUST Campus Navigation System
Run with:  streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── page config (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="KNUST Campus Navigator",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── fonts & base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2137 0%, #1565C0 100%);
    color: white;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: white !important;
}
[data-testid="stSidebar"] .stRadio > div {
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 4px;
}

/* ── metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #E3F2FD, #FFFFFF);
    border: 1px solid #BBDEFB;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    color: #0D2137 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    color: #546E7A !important;
    font-weight: 600 !important;
}

/* ── buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1565C0, #0288D1);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: 0 4px 14px rgba(21,101,192,0.35);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(21,101,192,0.45);
    background: linear-gradient(135deg, #0D47A1, #0277BD);
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #E3F2FD;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    color: #1565C0;
}
.stTabs [aria-selected="true"] {
    background: #1565C0 !important;
    color: white !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── selectbox ── */
.stSelectbox > div > div {
    border-radius: 8px;
    border: 1.5px solid #BBDEFB;
}

/* ── expander ── */
details {
    background: #F8FAFC;
    border: 1px solid #BBDEFB;
    border-radius: 10px;
}

/* ── divider ── */
hr {
    border: none;
    border-top: 2px solid #E3F2FD;
    margin: 18px 0;
}

/* ── success / info / warning ── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── init session state ────────────────────────────────────────────────
from streamlit_utils import init_state
init_state()

# ── sidebar navigation ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 8px 0 16px 0;'>
        <div style='font-size:2.4rem;'>🗺</div>
        <div style='font-size:1.1rem; font-weight:800; color:white; letter-spacing:0.5px;'>
            KNUST Campus Navigator
        </div>
        <div style='font-size:0.72rem; color:#90CAF9; margin-top:3px;'>
            COE 363 · Group 13 · DSA Project
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        options=[
            "🗺  Find Path",
            "📊  Compare Algorithms",
            "📚  Learn Algorithms",
            "⚙️  Manage Graph",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    g = st.session_state.graph
    stats = g.stats()
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.1); border-radius:10px; padding:12px 14px;'>
        <div style='color:#90CAF9; font-size:0.72rem; font-weight:700; letter-spacing:1px;
                    text-transform:uppercase; margin-bottom:8px;'>Campus Stats</div>
        <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
            <span style='color:white; font-size:0.88rem;'>📍 Locations</span>
            <span style='color:#FFD600; font-weight:800;'>{stats['nodes']}</span>
        </div>
        <div style='display:flex; justify-content:space-between;'>
            <span style='color:white; font-size:0.88rem;'>🔗 Paths</span>
            <span style='color:#FFD600; font-weight:800;'>{stats['edges']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── route to pages ────────────────────────────────────────────────────
if "Find Path" in page:
    from pages_nav.page_navigate import render
    render()
elif "Compare" in page:
    from pages_nav.page_compare import render
    render()
elif "Learn" in page:
    from pages_nav.page_learn import render
    render()
elif "Manage" in page:
    from pages_nav.page_manage import render
    render()