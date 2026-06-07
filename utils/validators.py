"""
Invoice validation – GST format check, maths audit, duplicate detection.
"""
from __future__ import annotations
import re
from utils.db import fetch_all, _num


# GST numbers follow the pattern: 2-digit state code + 10-char PAN + 1 entity code + 'Z' + checksum
GST_PATTERN = re.compile(
    r"^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
)


def validate_gst_format(gst: str) -> tuple[bool, str]:
    if not gst:
        return False, "GST number missing"
    gst = gst.strip().upper()
    if not GST_PATTERN.match(gst):
        return False, f"Invalid GST format: {gst}"
    return True, "Valid format"


def audit_maths(fields: dict) -> list[str]:
    """Return a list of arithmetic errors found in the extracted fields."""
    errors = []
    line_items = fields.get("line_items", [])

    # Prefer a dedicated subtotal field; fall back to total_amount
    subtotal = _num(fields.get("subtotal") or fields.get("total_amount", 0))
    gst_amt  = _num(fields.get("gst_amount", 0))
    total    = _num(fields.get("total_amount", 0))

    # Check that line items add up to the subtotal
    if line_items:
        computed = sum(_num(i.get("amount", 0)) for i in line_items)
        if computed > 0 and abs(computed - subtotal) > 5:
            errors.append(
                f"Line items sum ₹{computed:,.2f} ≠ subtotal ₹{subtotal:,.2f}"
            )

    # Check subtotal + GST = total
    if subtotal > 0 and gst_amt > 0:
        expected = subtotal + gst_amt
        if abs(expected - total) > 5:
            errors.append(
                f"Subtotal ₹{subtotal:,.2f} + GST ₹{gst_amt:,.2f} = "
                f"₹{expected:,.2f} but invoice total is ₹{total:,.2f}"
            )

    return errors


def check_duplicate(invoice_no: str, inv_type: str) -> bool:
    """Return True if this invoice number already exists in the database."""
    if not invoice_no:
        return False
    existing = fetch_all(inv_type)
    return any(
        r["invoice_no"].strip().lower() == invoice_no.strip().lower()
        for r in existing
        if r["invoice_no"]
    )


def run_all_checks(fields: dict, inv_type: str) -> tuple[bool, str]:
    """
    Run all validations and return (flagged, reason_string).
    flagged is True if any check failed.
    """
    reasons = []

    gst_ok, gst_msg = validate_gst_format(fields.get("gst_number", ""))
    if not gst_ok:
        reasons.append(gst_msg)

    reasons.extend(audit_maths(fields))

    if check_duplicate(fields.get("invoice_no", ""), inv_type):
        reasons.append(f"Duplicate invoice number: {fields.get('invoice_no')}")

    flagged = bool(reasons)
    return flagged, " | ".join(reasons) if reasons else ""
