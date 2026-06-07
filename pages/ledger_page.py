"""
GST Ledger – month-wise breakdown of purchases, sales, ITC, and net payable.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_monthly_data, fetch_all
from utils.csv_export import export_selected


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>GST Ledger</div>
        <div class='page-subtitle'>Month-wise GST summary — purchases, sales, ITC, and net payable</div>
    </div>
    """, unsafe_allow_html=True)

    monthly = get_monthly_data()

    if not monthly:
        st.markdown("""
        <div class='info-box' style='text-align:center;padding:60px 20px'>
            <div style='font-size:48px;margin-bottom:16px'>📒</div>
            <div style='font-size:16px;font-weight:600;color:#6b6258'>No ledger data yet</div>
            <div style='font-size:13px;color:#9e9590;margin-top:8px'>Upload invoices to see your GST ledger</div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(monthly)
    df["gst_payable"] = (df["gst_collected"] - df["gst_paid"]).clip(lower=0)
    df["profit"]      = df["sales"] - df["purchases"]

    # ── Trend chart ────────────────────────────────────────────────────────────
    fig = go.Figure()
    fig.add_scatter(x=df["month"], y=df["sales"],         name="Sales",         line=dict(color="#3b4fa8", width=2), mode="lines+markers")
    fig.add_scatter(x=df["month"], y=df["purchases"],     name="Purchases",     line=dict(color="#1a7f6e", width=2), mode="lines+markers")
    fig.add_scatter(x=df["month"], y=df["gst_collected"], name="GST Collected", line=dict(color="#b84040", width=2, dash="dot"), mode="lines+markers")
    fig.add_scatter(x=df["month"], y=df["gst_paid"],      name="ITC (GST Paid)", line=dict(color="#b07a20", width=2, dash="dot"), mode="lines+markers")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_family="Instrument Sans", plot_bgcolor="rgba(250,247,242,0)",
        font_color="#6b6258", legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=0), height=300,
    )
    fig.update_yaxes(gridcolor="#ddd5c8")
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── Summary table ──────────────────────────────────────────────────────────
    st.markdown("<div class='card-title'>📋 Month-wise GST Ledger</div>", unsafe_allow_html=True)
    df_show = df.copy()
    for col in ["sales", "purchases", "gst_collected", "gst_paid", "gst_payable", "profit"]:
        df_show[col] = df_show[col].apply(lambda x: f"₹{x:,.2f}")
    df_show.rename(columns={
        "month": "Month", "sales": "Sales", "purchases": "Purchases",
        "gst_collected": "GST Collected", "gst_paid": "ITC (GST Paid)",
        "gst_payable": "Net GST Payable", "profit": "Gross Profit",
    }, inplace=True)
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ── Per-month detail ───────────────────────────────────────────────────────
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>🔍 Month Detail</div>", unsafe_allow_html=True)
    months = [r["month"] for r in monthly]
    selected_month = st.selectbox("Select month", months)

    all_inv    = fetch_all()
    month_inv  = [r for r in all_inv if r["created_at"][:7] == selected_month]

    if month_inv:
        df_inv = pd.DataFrame(month_inv)[
            ["type", "vendor_name", "invoice_no", "total_amount", "gst_amount", "flagged"]
        ].copy()
        df_inv.rename(columns={
            "type": "Type", "vendor_name": "Vendor/Customer",
            "invoice_no": "Invoice No.", "total_amount": "Total (₹)",
            "gst_amount": "GST (₹)", "flagged": "Flag",
        }, inplace=True)
        df_inv["Flag"]      = df_inv["Flag"].apply(lambda x: "⚠️" if x else "✅")
        df_inv["Total (₹)"] = df_inv["Total (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        df_inv["GST (₹)"]   = df_inv["GST (₹)"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(df_inv, use_container_width=True, hide_index=True)

        month_ids = [r["id"] for r in month_inv]
        st.download_button(
            f"⬇️ Export {selected_month} Invoices CSV",
            data=export_selected(month_ids),
            file_name=f"gst_ledger_{selected_month}.csv",
            mime="text/csv",
        )
    else:
        st.info(f"No invoices found for {selected_month}.")
