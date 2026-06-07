"""
Centralised session-state helpers so every page reads from the same store.
"""
from __future__ import annotations
import streamlit as st
from datetime import datetime


def init_state():
    defaults = {
        # API settings
        "api_key": "",
        # Currently loaded invoice
        "current_file_bytes": None,
        "current_filename": "",
        "current_ocr_text": "",
        "current_fields": {},
        "current_summary": "",
        "current_category": {},
        # Chat history for Q&A page
        "qa_history": [],
        # Persistent invoice history list
        "invoice_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_to_history():
    """Snapshot the current invoice into the history list."""
    fields = st.session_state.get("current_fields", {})
    record = {
        "timestamp":  datetime.now().strftime("%d %b %Y, %H:%M"),
        "filename":   st.session_state.get("current_filename") or "—",
        "vendor":     fields.get("vendor_name") or "—",
        # The extraction prompt uses 'invoice_number', not 'invoice_no'
        "invoice_no": fields.get("invoice_number") or "—",
        "date":       fields.get("invoice_date") or "—",
        "total":      fields.get("total_amount") or "—",
        "gst":        fields.get("gst_amount") or "—",
        "category":   st.session_state.get("current_category", {}).get("category") or "—",
        "summary":    st.session_state.get("current_summary", ""),
    }
    history: list = st.session_state.get("invoice_history", [])
    history.insert(0, record)
    st.session_state.invoice_history = history
