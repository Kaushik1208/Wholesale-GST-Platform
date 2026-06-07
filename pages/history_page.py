"""
History page – all invoices analysed in this session (session-state backed).
"""
from __future__ import annotations
import re
import streamlit as st
import pandas as pd
from utils.state import init_state


def _parse_amount(raw) -> float:
    """Try to extract a float from a raw amount string."""
    if raw is None:
        return 0.0
    nums = re.findall(r"[\d,]+\.?\d*", str(raw).replace(",", ""))
    try:
        return float(nums[0]) if nums else 0.0
    except (ValueError, IndexError):
        return 0.0


def render():
    init_state()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Invoice History</div>
        <div class='page-subtitle'>All invoices analysed in this session</div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.get("invoice_history", [])

    if not history:
        st.markdown("""
        <div class='info-box' style='text-align:center;padding:60px 20px;background:var(--paper-2);border:1px solid var(--rule);border-radius:4px'>
            <div style='font-size:48px;margin-bottom:16px'>🗂️</div>
            <div style='font-size:16px;font-weight:600;color:#6b6258'>No history yet</div>
            <div style='font-size:13px;color:#9e9590;margin-top:8px'>
                Analyse invoices to see them listed here.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Summary stats ──────────────────────────────────────────────────────────
    total_count  = len(history)
    amounts      = [_parse_amount(r.get("total")) for r in history]
    unique_vendors = len({r.get("vendor", "—") for r in history})

    st.markdown(f"""
    <div class='metric-grid'>
        <div class='metric-card blue'>
            <div class='metric-icon'>📄</div>
            <div class='metric-label'>Total Invoices</div>
            <div class='metric-value'>{total_count}</div>
        </div>
        <div class='metric-card green'>
            <div class='metric-icon'>💰</div>
            <div class='metric-label'>Total Value (parsed)</div>
            <div class='metric-value'>₹ {sum(amounts):,.2f}</div>
        </div>
        <div class='metric-card amber'>
            <div class='metric-icon'>🏪</div>
            <div class='metric-label'>Unique Vendors</div>
            <div class='metric-value'>{unique_vendors}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── Summary table ──────────────────────────────────────────────────────────
    display_cols = ["timestamp", "filename", "vendor", "invoice_no", "date", "total", "gst", "category"]
    df = pd.DataFrame(history)[display_cols]
    df.columns = ["Time", "File", "Vendor", "Invoice No.", "Date", "Total", "GST", "Category"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── Detail cards ───────────────────────────────────────────────────────────
    st.markdown("<div class='card-title'>📋 Invoice Summaries</div>", unsafe_allow_html=True)
    for rec in history:
        label = f"{rec['timestamp']}  ·  {rec['filename']}  ·  {rec['vendor']}"
        with st.expander(label, expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Vendor:** {rec['vendor']}")
                st.markdown(f"**Invoice No.:** {rec['invoice_no']}")
                st.markdown(f"**Date:** {rec['date']}")
            with c2:
                st.markdown(f"**Total:** {rec['total']}")
                st.markdown(f"**GST:** {rec['gst']}")
                st.markdown(f"**Category:** {rec['category']}")
            if rec.get("summary"):
                st.markdown("---")
                st.markdown(f"<div class='summary-box'>{rec['summary']}</div>", unsafe_allow_html=True)

    if st.button("🗑️  Clear History", use_container_width=False):
        st.session_state.invoice_history = []
        st.rerun()
