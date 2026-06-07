"""
Invoice Q&A – ask questions about any saved invoice using AI.
"""
from __future__ import annotations
import streamlit as st
from utils.db import fetch_all
from utils.gemini_utils import answer_question


SAMPLE_QUESTIONS = [
    "What is the total GST amount?",
    "Who is the vendor / customer?",
    "What products were purchased?",
    "What is the invoice number and date?",
    "Is the GST number valid?",
    "Give me a breakdown of all line items.",
]


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-title'>Invoice Q&A Assistant</div>
        <div class='page-subtitle'>Ask anything about any saved invoice</div>
    </div>
    """, unsafe_allow_html=True)

    all_inv = fetch_all()
    if not all_inv:
        st.markdown(
            "<div class='info-box' style='text-align:center;padding:60px'>No invoices saved yet. Upload one first.</div>",
            unsafe_allow_html=True,
        )
        return

    id_labels = {
        r["id"]: f"#{r['id']} – {r['type'].upper()} – {r['vendor_name'] or 'Unknown'} – ₹{r['total_amount']:,.2f}"
        for r in all_inv
    }
    selected_id  = st.selectbox("Select Invoice", options=[r["id"] for r in all_inv], format_func=lambda x: id_labels[x])
    selected_inv = next(r for r in all_inv if r["id"] == selected_id)

    st.markdown(f"""
    <div class='info-box' style='margin-bottom:16px'>
        <strong>{selected_inv['vendor_name'] or 'Unknown'}</strong> &nbsp;·&nbsp;
        {selected_inv['invoice_no'] or '—'} &nbsp;·&nbsp;
        ₹{selected_inv['total_amount']:,.2f} &nbsp;·&nbsp;
        {selected_inv['type'].upper()}
    </div>
    """, unsafe_allow_html=True)

    # Use the saved AI summary as context (avoids re-running OCR)
    context = selected_inv.get("summary") or (
        f"Invoice from {selected_inv['vendor_name']}, "
        f"total ₹{selected_inv['total_amount']}, "
        f"GST ₹{selected_inv['gst_amount']}, "
        f"date {selected_inv['invoice_date']}"
    )

    # ── Quick question buttons ─────────────────────────────────────────────────
    st.markdown("<div class='card-title'>💡 Quick Questions</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    selected_quick = None
    for i, q in enumerate(SAMPLE_QUESTIONS):
        if cols[i % 3].button(q, key=f"qq_{i}", use_container_width=True):
            selected_quick = q

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Per-invoice Q&A history (keyed by invoice ID so switching invoices clears it)
    hist_key = f"qa_hist_{selected_id}"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []

    for turn in st.session_state[hist_key]:
        st.markdown(f"<div class='msg-label'>You</div><div class='msg-user'>{turn['q']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='msg-label'>AI</div><div class='msg-ai'>{turn['a']}</div>", unsafe_allow_html=True)

    user_q = st.text_input(
        "Ask a question",
        value=selected_quick or "",
        placeholder="e.g. What is the total amount?",
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([1, 5])
    with c1:
        ask = st.button("Ask →", use_container_width=True)
    with c2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state[hist_key] = []
            st.rerun()

    if ask and user_q:
        if not st.session_state.get("api_key"):
            st.error("⚠️ API key not configured.")
        else:
            with st.spinner("Thinking…"):
                try:
                    ans = answer_question(context, user_q, st.session_state.api_key)
                    st.session_state[hist_key].append({"q": user_q, "a": ans})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
