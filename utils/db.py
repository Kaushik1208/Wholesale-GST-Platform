"""
SQLite database layer for the Wholesale GST Platform.
Stores purchase and sales invoices persistently.
"""
from __future__ import annotations
import sqlite3
import json
import re
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "wholesale_gst.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS invoices (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            type         TEXT NOT NULL CHECK(type IN ('purchase','sales')),
            filename     TEXT,
            vendor_name  TEXT,
            invoice_no   TEXT,
            invoice_date TEXT,
            gst_number   TEXT,
            subtotal     REAL DEFAULT 0,
            gst_amount   REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            gst_rate     REAL DEFAULT 18,
            category     TEXT DEFAULT 'Miscellaneous',
            status       TEXT DEFAULT 'Unverified',
            flagged      INTEGER DEFAULT 0,
            flag_reason  TEXT,
            line_items   TEXT DEFAULT '[]',
            summary      TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now','localtime'))
        );
    """)
    conn.commit()
    conn.close()


# ── CRUD ───────────────────────────────────────────────────────────────────────

def insert_invoice(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO invoices
        (type, filename, vendor_name, invoice_no, invoice_date, gst_number,
         subtotal, gst_amount, total_amount, gst_rate, category,
         status, flagged, flag_reason, line_items, summary)
        VALUES (:type,:filename,:vendor_name,:invoice_no,:invoice_date,:gst_number,
                :subtotal,:gst_amount,:total_amount,:gst_rate,:category,
                :status,:flagged,:flag_reason,:line_items,:summary)
    """, {
        "type":         data.get("type", "purchase"),
        "filename":     data.get("filename", ""),
        "vendor_name":  data.get("vendor_name", ""),
        "invoice_no":   data.get("invoice_no", ""),
        "invoice_date": data.get("invoice_date", ""),
        "gst_number":   data.get("gst_number", ""),
        "subtotal":     _num(data.get("subtotal", 0)),
        "gst_amount":   _num(data.get("gst_amount", 0)),
        "total_amount": _num(data.get("total_amount", 0)),
        "gst_rate":     _num(data.get("gst_rate", 18)),
        "category":     data.get("category", "Miscellaneous"),
        "status":       data.get("status", "Unverified"),
        "flagged":      1 if data.get("flagged") else 0,
        "flag_reason":  data.get("flag_reason", ""),
        "line_items":   json.dumps(data.get("line_items", [])),
        "summary":      data.get("summary", ""),
    })
    row_id = c.lastrowid
    conn.commit()
    conn.close()
    return row_id


def fetch_all(inv_type: str | None = None) -> list[dict]:
    conn = get_conn()
    c = conn.cursor()
    if inv_type:
        c.execute("SELECT * FROM invoices WHERE type=? ORDER BY created_at DESC", (inv_type,))
    else:
        c.execute("SELECT * FROM invoices ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def fetch_by_ids(ids: list[int]) -> list[dict]:
    if not ids:
        return []
    conn = get_conn()
    c = conn.cursor()
    placeholders = ",".join("?" * len(ids))
    c.execute(f"SELECT * FROM invoices WHERE id IN ({placeholders})", ids)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def delete_invoice(inv_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM invoices WHERE id=?", (inv_id,))
    conn.commit()
    conn.close()


def get_summary_stats() -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT
            SUM(CASE WHEN type='purchase' THEN total_amount ELSE 0 END) as total_purchase,
            SUM(CASE WHEN type='sales'    THEN total_amount ELSE 0 END) as total_sales,
            SUM(CASE WHEN type='purchase' THEN gst_amount   ELSE 0 END) as gst_paid,
            SUM(CASE WHEN type='sales'    THEN gst_amount   ELSE 0 END) as gst_collected,
            COUNT(CASE WHEN type='purchase' THEN 1 END) as purchase_count,
            COUNT(CASE WHEN type='sales'    THEN 1 END) as sales_count,
            COUNT(CASE WHEN flagged=1       THEN 1 END) as flagged_count
        FROM invoices
    """)
    row = dict(c.fetchone())
    conn.close()

    # Replace None with 0 for all numeric fields
    for k in row:
        if row[k] is None:
            row[k] = 0

    row["itc"]         = row["gst_paid"]
    row["gst_payable"] = max(0.0, row["gst_collected"] - row["gst_paid"])
    row["profit"]      = row["total_sales"] - row["total_purchase"]
    return row


def get_monthly_data() -> list[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT
            strftime('%Y-%m', created_at) as month,
            SUM(CASE WHEN type='purchase' THEN total_amount ELSE 0 END) as purchases,
            SUM(CASE WHEN type='sales'    THEN total_amount ELSE 0 END) as sales,
            SUM(CASE WHEN type='purchase' THEN gst_amount   ELSE 0 END) as gst_paid,
            SUM(CASE WHEN type='sales'    THEN gst_amount   ELSE 0 END) as gst_collected
        FROM invoices
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_vendor_stats() -> list[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT vendor_name,
               COUNT(*) as invoice_count,
               SUM(total_amount) as total_spend,
               SUM(gst_amount) as total_gst,
               type
        FROM invoices
        WHERE vendor_name != ''
        GROUP BY vendor_name, type
        ORDER BY total_spend DESC
        LIMIT 10
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ── helpers ────────────────────────────────────────────────────────────────────

def _num(val) -> float:
    """Safely convert a value to float, stripping currency symbols and commas."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    nums = re.findall(r"[\d]+\.?\d*", str(val).replace(",", ""))
    return float(nums[0]) if nums else 0.0
