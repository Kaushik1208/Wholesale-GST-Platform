"""
Purchase Invoices page – view, filter, select and export purchase invoices.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.db import fetch_all, delete_invoice
from utils.csv_export import export_selected, export_all


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Purchase Invoices</div>
        <div class='page-subtitle'>All invoices received from suppliers</div>
    </div>
    """, unsafe_allow_html=True)

    rows = fetch_all("purchase")

    if not rows:
        st.markdown("""
        <div class='info-box' style='text-align:center;padding:60px 20px;background:var(--paper-2);border:1px solid var(--rule);border-radius:4px'>
            <div style='font-size:48px;margin-bottom:16px'>📥</div>
            <div style='font-size:16px;font-weight:600;color:#6b6258'>No purchase invoices yet</div>
            <div style='font-size:13px;color:#9e9590;margin-top:8px'>
                Go to <strong>Upload & Analyse</strong> and select type <strong>Purchase</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Filters ────────────────────────────────────────────────────────────────
    with st.expander("🔍 Filter Invoices", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        vendor_filter   = fc1.text_input("Vendor Name contains", "")
        category_filter = fc2.selectbox("Category", ["All"] + sorted({r["category"] for r in rows if r["category"]}))
        flagged_filter  = fc3.selectbox("Status", ["All", "Flagged only", "Clean only"])

    filtered = rows
    if vendor_filter:
        filtered = [r for r in filtered if vendor_filter.lower() in (r["vendor_name"] or "").lower()]
    if category_filter != "All":
        filtered = [r for r in filtered if r["category"] == category_filter]
    if flagged_filter == "Flagged only":
        filtered = [r for r in filtered if r["flagged"]]
    elif flagged_filter == "Clean only":
        filtered = [r for r in filtered if not r["flagged"]]

    st.markdown(
        f"<div style='font-size:13px;color:#6b6258;margin-bottom:12px'>Showing {len(filtered)} of {len(rows)} invoices</div>",
        unsafe_allow_html=True,
    )

    # ── Invoice table ──────────────────────────────────────────────────────────
    if filtered:
        df = pd.DataFrame(filtered)
        display_cols = ["id", "vendor_name", "invoice_no", "invoice_date", "gst_number",
                        "subtotal", "gst_amount", "total_amount", "category", "flagged", "created_at"]
        available = [c for c in display_cols if c in df.columns]
        df_show = df[available].copy()
        df_show.rename(columns={
            "id": "ID", "vendor_name": "Vendor", "invoice_no": "Invoice No.",
            "invoice_date": "Date", "gst_number": "GST No.",
            "subtotal": "Subtotal", "gst_amount": "GST Amt", "total_amount": "Total",
            "category": "Category", "flagged": "Flag", "created_at": "Uploaded",
        }, inplace=True)
        if "Flag" in df_show.columns:
            df_show["Flag"] = df_show["Flag"].apply(lambda x: "⚠️" if x else "✅")
        for col in ("Total", "Subtotal", "GST Amt"):
            if col in df_show.columns:
                df_show[col] = df_show[col].apply(lambda x: f"₹{float(x):,.2f}" if x else "—")
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No invoices match the current filters.")

    # ── Export options ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>⬇️ Export Options</div>", unsafe_allow_html=True)

    all_ids   = [r["id"] for r in filtered]
    id_labels = {
        r["id"]: f"#{r['id']} – {r['vendor_name'] or 'Unknown'} – ₹{r['total_amount']:,.2f}"
        for r in filtered
    }

    selected_ids = st.multiselect(
        "Select specific invoices to export (leave empty to export all filtered)",
        options=all_ids,
        format_func=lambda x: id_labels[x],
    )

    c1, c2 = st.columns(2, gap="small")
    with c1:
        export_ids = selected_ids if selected_ids else all_ids
        csv_data   = export_selected(export_ids) if export_ids else b""
        label      = f"⬇️ Export {'Selected' if selected_ids else 'All Filtered'} ({len(export_ids)} invoices)"
        st.download_button(
            label,
            data=csv_data,
            file_name="purchase_invoices_export.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not export_ids,
        )
    with c2:
        st.download_button(
            "⬇️ Export All Purchase Invoices",
            data=export_all("purchase"),
            file_name="all_purchase_invoices.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Delete invoice ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    with st.expander("🗑️ Delete Invoice", expanded=False):
        if all_ids:
            del_id = st.selectbox("Select invoice to delete", options=all_ids, format_func=lambda x: id_labels[x])
            if st.button("Delete Selected Invoice", use_container_width=False):
                delete_invoice(del_id)
                st.success(f"Invoice #{del_id} deleted.")
                st.rerun()
        else:
            st.info("No invoices to delete.")
