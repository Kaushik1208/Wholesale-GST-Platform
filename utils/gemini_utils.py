"""
Groq API helpers – invoice extraction, summary, categorisation, and Q&A.
Uses llama-3.3-70b-versatile via Groq's API.
"""
from __future__ import annotations
import json
import re
from groq import Groq


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def _chat(client: Groq, prompt: str, max_tokens: int = 1500) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def _safe_json(text: str) -> dict:
    """Strip markdown code fences and parse JSON safely, returning {} on failure."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        return {}


# ── 1. Structured field extraction ────────────────────────────────────────────

EXTRACTION_PROMPT = """\
You are an expert invoice parser. Given the raw OCR text of an invoice, extract the following fields.
Return ONLY a JSON object with these exact keys (use null for any field not found):
{{
  "vendor_name": "...",
  "invoice_number": "...",
  "invoice_date": "...",
  "gst_number": "...",
  "total_amount": "...",
  "gst_amount": "...",
  "line_items": [ {{"description": "...", "qty": "...", "unit_price": "...", "amount": "..."}} ]
}}

OCR TEXT:
{text}
"""

def extract_invoice_fields(ocr_text: str, api_key: str) -> dict:
    client = _get_client(api_key)
    raw = _chat(client, EXTRACTION_PROMPT.format(text=ocr_text[:6000]))
    return _safe_json(raw)


# ── 2. Business summary ────────────────────────────────────────────────────────

SUMMARY_PROMPT = """\
You are a professional financial analyst. Write a concise business-friendly summary of this invoice.
Cover: vendor info, what was purchased, total cost breakdown, GST details, and any important notes.
Keep it to 4-6 sentences and be specific with numbers.

OCR TEXT:
{text}
"""

def generate_summary(ocr_text: str, api_key: str) -> str:
    client = _get_client(api_key)
    return _chat(client, SUMMARY_PROMPT.format(text=ocr_text[:5000]))


# ── 3. Expense categorisation ──────────────────────────────────────────────────

CATEGORY_PROMPT = """\
Classify this invoice into exactly ONE of these expense categories:
Office Supplies | Electronics | Furniture | Transportation | Food & Beverages |
Utilities | Software & Subscriptions | Medical | Miscellaneous

Return ONLY a JSON object: {{"category": "...", "confidence": "High/Medium/Low", "reason": "..."}}

OCR TEXT:
{text}
"""

def categorise_invoice(ocr_text: str, api_key: str) -> dict:
    client = _get_client(api_key)
    raw = _chat(client, CATEGORY_PROMPT.format(text=ocr_text[:3000]))
    data = _safe_json(raw)
    if not data.get("category"):
        data["category"] = "Miscellaneous"
    return data


# ── 4. Invoice Q&A ─────────────────────────────────────────────────────────────

QA_PROMPT = """\
You are an invoice assistant. Answer the user's question strictly based on the invoice text below.
Be concise, accurate, and professional. If the answer is not in the invoice, say so clearly.

INVOICE TEXT:
{text}

USER QUESTION:
{question}
"""

def answer_question(ocr_text: str, question: str, api_key: str) -> str:
    client = _get_client(api_key)
    return _chat(client, QA_PROMPT.format(text=ocr_text[:5000], question=question))
