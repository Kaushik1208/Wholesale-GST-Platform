"""
GST Dashboard – financial overview for the wholesale shop.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_summary_stats, get_monthly_data, get_vendor_stats, fetch_all
from utils.csv_export import export_all


def _fmt(val: float) -> str:
    return f"₹{val:,.2f}"


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>GST Dashboard</div>
        <div class='page-subtitle'>Complete financial overview for your wholesale shop</div>
    </div>
    """, unsafe_allow_html=True)

    stats = get_summary_stats()

    profit_color = "#00e5b0" if stats["profit"] >= 0 else "#ff6b6b"
    profit_label = "▲ Profit" if stats["profit"] >= 0 else "▼ Loss"

    # ── Top metric cards ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='metric-grid'>
        <div class='metric-card blue'>
            <div class='metric-icon'>📤</div>
            <div class='metric-label'>Total Sales</div>
            <div class='metric-value'>{_fmt(stats['total_sales'])}</div>
            <div style='font-size:11px;color:#9e9590;margin-top:4px'>{stats['sales_count']} invoices</div>
        </div>
        <div class='metric-card green'>
            <div class='metric-icon'>📥</div>
            <div class='metric-label'>Total Purchases</div>
            <div class='metric-value'>{_fmt(stats['total_purchase'])}</div>
            <div style='font-size:11px;color:#9e9590;margin-top:4px'>{stats['purchase_count']} invoices</div>
        </div>
        <div class='metric-card amber'>
            <div class='metric-icon'>💰</div>
            <div class='metric-label'>Gross Profit</div>
            <div class='metric-value'>{_fmt(stats['profit'])}</div>
            <div style='font-size:11px;color:{profit_color};margin-top:4px'>{profit_label}</div>
        </div>
        <div class='metric-card purple'>
            <div class='metric-icon'>🏦</div>
            <div class='metric-label'>GST Payable</div>
            <div class='metric-value'>{_fmt(stats['gst_payable'])}</div>
            <div style='font-size:11px;color:#9e9590;margin-top:4px'>After ITC deduction</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ITC breakdown ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='card' style='margin-bottom:24px'>
        <div class='card-title'>🧮 Input Tax Credit (ITC) Calculation</div>
        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center'>
            <div>
                <div style='font-size:12px;color:#6b6258;margin-bottom:6px'>GST Collected (Sales)</div>
                <div style='font-size:20px;font-weight:700;color:#b84040'>{_fmt(stats['gst_collected'])}</div>
            </div>
            <div style='display:flex;align-items:center;justify-content:center;font-size:28px;color:#9e9590'>−</div>
            <div>
                <div style='font-size:12px;color:#6b6258;margin-bottom:6px'>GST Paid on Purchases (ITC)</div>
                <div style='font-size:20px;font-weight:700;color:#1a7f6e'>{_fmt(stats['gst_paid'])}</div>
            </div>
        </div>
        <div style='border-top:1px solid #ddd5c8;margin-top:16px;padding-top:16px;text-align:center'>
            <div style='font-size:12px;color:#6b6258;margin-bottom:6px'>Net GST Payable to Government</div>
            <div style='font-size:28px;font-weight:800;color:#b07a20'>{_fmt(stats['gst_payable'])}</div>
            <div style='font-size:12px;color:#9e9590;margin-top:4px'>
                You save {_fmt(stats["itc"])} in ITC this period
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    monthly      = get_monthly_data()
    vendor_stats = get_vendor_stats()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<div class='card-title'>📈 Monthly Sales vs Purchases</div>", unsafe_allow_html=True)
        if monthly:
            df_m = pd.DataFrame(monthly)
            fig = go.Figure()
            fig.add_bar(x=df_m["month"], y=df_m["sales"],     name="Sales",     marker_color="#3b4fa8")
            fig.add_bar(x=df_m["month"], y=df_m["purchases"], name="Purchases", marker_color="#1a7f6e")
            fig.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#8892a4", legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0), height=260,
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(gridcolor="#ddd5c8")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                "<div class='info-box' style='text-align:center;padding:40px'>No data yet</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("<div class='card-title'>🥧 GST Breakdown</div>", unsafe_allow_html=True)
        if stats["gst_collected"] > 0 or stats["gst_paid"] > 0:
            fig2 = go.Figure(go.Pie(
                labels=["GST Collected (Sales)", "ITC (Purchases)", "Net Payable"],
                values=[stats["gst_collected"], stats["gst_paid"], stats["gst_payable"]],
                hole=0.55,
                marker_colors=["#b84040", "#1a7f6e", "#b07a20"],
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color="#6b6258", font_family="Instrument Sans",
                showlegend=True, legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=0, t=10, b=0), height=260,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(
                "<div class='info-box' style='text-align:center;padding:40px'>No GST data yet</div>",
                unsafe_allow_html=True,
            )

    # ── Top vendors / customers ────────────────────────────────────────────────
    if vendor_stats:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>🏪 Top Vendors / Customers</div>", unsafe_allow_html=True)
        df_v = pd.DataFrame(vendor_stats)
        df_v.columns = ["Vendor/Customer", "Invoices", "Total (₹)", "GST (₹)", "Type"]
        df_v["Total (₹)"] = df_v["Total (₹)"].apply(lambda x: f"₹{x:,.2f}")
        df_v["GST (₹)"]   = df_v["GST (₹)"].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(df_v, use_container_width=True, hide_index=True)

    # ── Flagged invoices ───────────────────────────────────────────────────────
    all_inv = fetch_all()
    flagged = [r for r in all_inv if r["flagged"]]
    if flagged:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>🚨 Flagged Invoices ({len(flagged)})</div>", unsafe_allow_html=True)
        for inv in flagged:
            st.markdown(f"""
            <div style='background:rgba(184,64,64,0.06);border:1px solid rgba(184,64,64,0.2);
                        border-radius:10px;padding:12px 16px;margin-bottom:8px'>
                <span style='color:#b84040;font-weight:600'>⚠️ {inv["vendor_name"] or "Unknown"}</span>
                &nbsp;·&nbsp;<span style='color:#6b6258;font-size:13px'>{inv["invoice_no"] or "No invoice no."}</span>
                &nbsp;·&nbsp;<span style='color:#6b6258;font-size:13px'>{inv["type"].upper()}</span><br>
                <span style='font-size:12px;color:#b84040;margin-top:4px;display:block'>{inv["flag_reason"]}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── CSV export ─────────────────────────────────────────────────────────────
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        st.download_button(
            "⬇️  Export All Invoices (CSV)",
            data=export_all(),
            file_name="all_invoices.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️  Export Purchase CSV",
            data=export_all("purchase"),
            file_name="purchase_invoices.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "⬇️  Export Sales CSV",
            data=export_all("sales"),
            file_name="sales_invoices.csv",
            mime="text/csv",
            use_container_width=True,
        )
