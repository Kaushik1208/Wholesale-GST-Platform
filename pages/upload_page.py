"""
Upload & Analyse page – OCR + AI extraction + validation + save to DB.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.ocr_utils import extract_text_from_bytes
from utils.gemini_utils import extract_invoice_fields, generate_summary, categorise_invoice
from utils.validators import run_all_checks
from utils.db import insert_invoice, _num


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Upload & Analyse Invoice</div>
        <div class='page-subtitle'>Upload a purchase or sales invoice — AI extracts, validates and saves it</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Invoice type selector ──────────────────────────────────────────────────
    inv_type = st.radio(
        "Invoice Type",
        ["purchase", "sales"],
        format_func=lambda x: "📥 Purchase (from supplier)" if x == "purchase" else "📤 Sales (to customer)",
        horizontal=True,
    )

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── File upload & preview ──────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("<div class='card-title'>📤 Upload Invoice</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed"
        )
        if uploaded:
            # Reset all previous state whenever a new file is uploaded
            st.session_state["up_bytes"]    = uploaded.read()
            st.session_state["up_filename"] = uploaded.name
            st.session_state["up_ocr"]      = ""
            st.session_state["up_fields"]   = {}
            st.session_state["up_summary"]  = ""
            st.session_state["up_category"] = {}
            size_kb = len(st.session_state["up_bytes"]) / 1024
            st.markdown(
                f"<div class='info-box'>📄 <strong>{uploaded.name}</strong><br>Size: {size_kb:.1f} KB</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("<div class='card-title'>🖼️ Preview</div>", unsafe_allow_html=True)
        if st.session_state.get("up_bytes"):
            fname = st.session_state.get("up_filename", "")
            if fname.lower().endswith(".pdf"):
                st.info("PDF uploaded — OCR will extract text from all pages.")
            else:
                st.image(st.session_state["up_bytes"], use_container_width=True)
        else:
            st.markdown(
                "<div class='info-box' style='text-align:center;padding:48px;color:#9e9590'>No file uploaded</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # ── Run pipeline ───────────────────────────────────────────────────────────
    if st.session_state.get("up_bytes"):
        if st.button("⚡  Run Full Pipeline & Save", use_container_width=True):
            if not st.session_state.get("api_key"):
                st.error("⚠️ API key not configured. Contact the app owner to set up the Groq API key.")
            else:
                progress = st.progress(0, text="Step 1/4 – Running OCR…")
                try:
                    # Step 1: OCR
                    ocr_text = extract_text_from_bytes(
                        st.session_state["up_bytes"],
                        st.session_state["up_filename"],
                    )
                    st.session_state["up_ocr"] = ocr_text
                    progress.progress(25, text="Step 2/4 – Extracting fields with AI…")

                    # Step 2: AI field extraction
                    key = st.session_state.api_key
                    fields = extract_invoice_fields(ocr_text, key)
                    st.session_state["up_fields"] = fields
                    progress.progress(50, text="Step 3/4 – Generating summary…")

                    # Step 3: Summary and category
                    summary  = generate_summary(ocr_text, key)
                    category = categorise_invoice(ocr_text, key)
                    st.session_state["up_summary"]  = summary
                    st.session_state["up_category"] = category
                    progress.progress(75, text="Step 4/4 – Validating & saving…")

                    # Step 4: Validate and persist
                    # The AI returns 'invoice_number'; DB stores it as 'invoice_no'
                    flagged, flag_reason = run_all_checks(
                        {**fields, "invoice_no": fields.get("invoice_number", "")},
                        inv_type,
                    )

                    # subtotal is not returned separately by the AI, so we compute it
                    total_amount = _num(fields.get("total_amount", 0))
                    gst_amount   = _num(fields.get("gst_amount", 0))
                    subtotal     = total_amount - gst_amount if total_amount > gst_amount else total_amount

                    record = {
                        "type":         inv_type,
                        "filename":     st.session_state["up_filename"],
                        "vendor_name":  fields.get("vendor_name") or "",
                        "invoice_no":   fields.get("invoice_number") or "",
                        "invoice_date": fields.get("invoice_date") or "",
                        "gst_number":   fields.get("gst_number") or "",
                        "subtotal":     subtotal,
                        "gst_amount":   gst_amount,
                        "total_amount": total_amount,
                        "gst_rate":     18,
                        "category":     category.get("category", "Miscellaneous"),
                        "status":       "Flagged" if flagged else "Verified",
                        "flagged":      flagged,
                        "flag_reason":  flag_reason,
                        "line_items":   fields.get("line_items", []),
                        "summary":      summary,
                    }
                    inv_id = insert_invoice(record)
                    progress.progress(100, text="Done!")

                    if flagged:
                        st.warning(f"⚠️ Invoice saved with flags: {flag_reason}")
                    else:
                        st.success(f"✅ Invoice #{inv_id} saved successfully!")

                except Exception as e:
                    st.error(f"Pipeline error: {e}")

    # ── Display results after pipeline runs ────────────────────────────────────
    if st.session_state.get("up_ocr"):
        with st.expander("📝 Extracted OCR Text", expanded=False):
            st.markdown(
                f"<div class='extracted-text'>{st.session_state['up_ocr']}</div>",
                unsafe_allow_html=True,
            )

    if st.session_state.get("up_fields"):
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>📋 Extracted Fields</div>", unsafe_allow_html=True)
        f = st.session_state["up_fields"]
        df = pd.DataFrame([
            ("Vendor / Customer", f.get("vendor_name") or "—"),
            ("Invoice Number",    f.get("invoice_number") or "—"),
            ("Invoice Date",      f.get("invoice_date") or "—"),
            ("GST Number",        f.get("gst_number") or "—"),
            ("Total Amount",      f.get("total_amount") or "—"),
            ("GST Amount",        f.get("gst_amount") or "—"),
        ], columns=["Field", "Value"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    if st.session_state.get("up_summary"):
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>✨ AI Summary</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='summary-box'>{st.session_state['up_summary']}</div>",
            unsafe_allow_html=True,
        )
