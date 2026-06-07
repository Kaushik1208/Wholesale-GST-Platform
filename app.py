import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="WholesaleGST",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Hide sidebar, override nav button colors to sit on dark bar
st.markdown("""
<style>
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }

/* Nav bar lives on ink background — override button colors there */
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #9e9590 !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 14px 4px !important;
    transition: color 0.15s, border-color 0.15s !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
    color: #faf7f2 !important;
    border-bottom-color: #c8b89a !important;
    background: transparent !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    color: #faf7f2 !important;
    border-bottom: 2px solid #c8b89a !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

from utils.db import init_db
init_db()

from utils.config import GROQ_API_KEY
from pages import gst_dashboard, purchase_page, sales_page, ledger_page, upload_page, qa_page

# Pre-load API key — no settings page needed
if "api_key" not in st.session_state:
    st.session_state.api_key = GROQ_API_KEY

# ── Top navigation ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='top-nav'>
  <div class='nav-brand'>Wholesale<span>GST</span></div>
</div>
""", unsafe_allow_html=True)

nav_items = {
    "Dashboard":  "dashboard",
    "Purchases":  "purchase",
    "Sales":      "sales",
    "GST Ledger": "ledger",
    "Upload":     "upload",
    "Q & A":      "qa",
}

if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"

cols = st.columns(len(nav_items))
for i, (label, key) in enumerate(nav_items.items()):
    is_active = st.session_state.active_page == key
    with cols[i]:
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.active_page = key
            st.rerun()

st.markdown("<div style='height:1px;background:#ddd5c8;margin:0 0 2rem'></div>", unsafe_allow_html=True)

# ── Route ──────────────────────────────────────────────────────────────────────
p = st.session_state.active_page
if   p == "dashboard": gst_dashboard.render()
elif p == "purchase":  purchase_page.render()
elif p == "sales":     sales_page.render()
elif p == "ledger":    ledger_page.render()
elif p == "upload":    upload_page.render()
elif p == "qa":        qa_page.render()
