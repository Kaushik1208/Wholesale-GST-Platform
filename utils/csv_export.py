"""
CSV export helpers for invoice data.
"""
from __future__ import annotations
import csv
import io
from utils.db import fetch_all, fetch_by_ids


COLUMNS = [
    "id", "type", "vendor_name", "invoice_no", "invoice_date",
    "gst_number", "subtotal", "gst_amount", "total_amount",
    "gst_rate", "category", "status", "flagged", "flag_reason", "created_at",
]

HEADERS = [
    "ID", "Type", "Vendor / Customer", "Invoice No.", "Invoice Date",
    "GST Number", "Subtotal (₹)", "GST Amount (₹)", "Total Amount (₹)",
    "GST Rate (%)", "Category", "Status", "Flagged", "Flag Reason", "Uploaded At",
]


def rows_to_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writerow(dict(zip(COLUMNS, HEADERS)))
    for r in rows:
        r["flagged"] = "Yes" if r.get("flagged") else "No"
        writer.writerow({c: r.get(c, "") for c in COLUMNS})
    # utf-8-sig adds a BOM so Excel opens the file correctly without garbled chars
    return buf.getvalue().encode("utf-8-sig")


def export_all(inv_type: str | None = None) -> bytes:
    return rows_to_csv(fetch_all(inv_type))


def export_selected(ids: list[int]) -> bytes:
    if not ids:
        return rows_to_csv([])
    return rows_to_csv(fetch_by_ids(ids))
