"""
Central config — reads API key from Streamlit secrets (deployed)
or from a .env file (local development).

Priority:
  1. st.secrets["GROQ_API_KEY"]   ← Streamlit Cloud / deployed
  2. os.environ["GROQ_API_KEY"]   ← local .env or shell export
  3. Hardcoded fallback (fill in during local dev only)
"""
from __future__ import annotations
import os

def _load_key() -> str:
    # 1. Try Streamlit secrets (works on Streamlit Cloud after you add the secret)
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # 2. Environment variable (local dev with .env or shell export)
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key

    # 3. Dev fallback — replace with your key for local testing only
    return ""


GROQ_API_KEY: str = _load_key()
