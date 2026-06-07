"""
Dashboard page – metrics and summary for the current invoice.
"""
from __future__ import annotations
import streamlit as st
from utils.state import init_state

CATEGORY_ICONS = {
    "Office Supplies": "🖊️", "Electronics": "💻", "Furniture": "🪑",
    "Transportation": "🚗", "Food & Beverages": "🍽️", "Utilities": "⚡",
    "Software & Subscriptions": "📦", "Medical": "🏥", "Miscellaneous": "📁",
}


def render():
    init_state()

    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Dashboard</div>
        <div class='page-subtitle'>Key metrics and insights for the current invoice</div>
    </div>
    """, unsafe_allow_html=True)

    fields = st.session_state.get("current_fields", {})
    category = st.session_state.get("current_category", {})
    summary = st.session_state.get("current_summary", "")
    filename = st.session_state.get("current_filename", "")

    if not fields:
        st.markdown("""
        <div class='info-box' style='text-align:center;padding:60px 20px;'>
            <div style='font-size:48px;margin-bottom:16px'>📊</div>
            <div style='font-size:16px;font-weight:600;color:#6b6258'>No invoice analysed yet</div>
            <div style='font-size:13px;color:#9e9590;margin-top:8px'>
                Upload and analyse an invoice on the <strong>Upload & Analyze</strong> page to see your dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Metrics row ──────────────────────────────────────────────────────────
    vendor = fields.get("vendor_name") or "—"
    total = fields.get("total_amount") or "—"
    gst = fields.get("gst_amount") or "—"
    gst_no = fields.get("gst_number") or "—"
    inv_no = fields.get("invoice_number") or "—"
    inv_date = fields.get("invoice_date") or "—"
    cat_name = category.get("category") or "—"
    cat_icon = CATEGORY_ICONS.get(cat_name, "📁")

    st.markdown(f"""
    <div class='metric-grid'>
        <div class='metric-card blue'>
            <div class='metric-icon'>💰</div>
            <div class='metric-label'>Total Amount</div>
            <div class='metric-value'>{total}</div>
        </div>
        <div class='metric-card green'>
            <div class='metric-icon'>🏦</div>
            <div class='metric-label'>GST Amount</div>
            <div class='metric-value'>{gst}</div>
        </div>
        <div class='metric-card amber'>
            <div class='metric-icon'>🏪</div>
            <div class='metric-label'>Vendor</div>
            <div class='metric-value' style='font-size:16px'>{vendor}</div>
        </div>
        <div class='metric-card purple'>
            <div class='metric-icon'>{cat_icon}</div>
            <div class='metric-label'>Category</div>
            <div class='metric-value' style='font-size:15px'>{cat_name}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Detail grid ──────────────────────────────────────────────────────────
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Invoice Details</div>", unsafe_allow_html=True)

        details = {
            "📄 File": filename,
            "🔢 Invoice No.": inv_no,
            "📅 Date": inv_date,
            "🏪 Vendor": vendor,
            "🪪 GST Number": gst_no,
        }
        for label, value in details.items():
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e2330'>
                <span style='color:#6b6258;font-size:13px'>{label}</span>
                <span style='color:#1a1612;font-size:13px;font-weight:500;text-align:right;max-width:200px'>{value}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Financial Summary</div>", unsafe_allow_html=True)

        fin_details = {
            "💰 Total Amount": total,
            "🏦 GST Amount": gst,
            "📦 Category": f"{cat_icon} {cat_name}",
            "📊 Confidence": category.get("confidence") or "—",
        }
        for label, value in fin_details.items():
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e2330'>
                <span style='color:#6b6258;font-size:13px'>{label}</span>
                <span style='color:#1a1612;font-size:13px;font-weight:500'>{value}</span>
            </div>
            """, unsafe_allow_html=True)

        reason = category.get("reason", "")
        if reason:
            st.markdown(f"<div style='margin-top:12px;font-size:12px;color:#9e9590;font-style:italic'>💡 {reason}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Summary ──────────────────────────────────────────────────────────────
    if summary:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>✨ AI Business Summary</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

    # ── Line items ───────────────────────────────────────────────────────────
    line_items = fields.get("line_items", [])
    if line_items:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>🛒 Line Items</div>", unsafe_allow_html=True)
        import pandas as pd
        li_df = pd.DataFrame(line_items)
        st.dataframe(li_df, use_container_width=True, hide_index=True)
