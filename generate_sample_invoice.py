"""
generate_sample_invoice.py
Run this script to create a sample_invoice.png you can use for testing.

Usage:
    python generate_sample_invoice.py
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

def make_invoice():
    W, H = 800, 1100
    img = Image.new("RGB", (W, H), color="#ffffff")
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, W, 100], fill="#1a237e")
    draw.text((40, 30), "TAX INVOICE", fill="white", font=None)
    draw.text((550, 20), "TECHMART SOLUTIONS PVT LTD", fill="white", font=None)
    draw.text((550, 45), "GST No: 27AAPCT1234F1Z5", fill="#bbdefb", font=None)
    draw.text((550, 65), "MH - 400001, Mumbai", fill="#bbdefb", font=None)

    # Invoice details
    y = 130
    draw.text((40, y), "Invoice No:  INV-2024-00847", fill="#111", font=None)
    draw.text((40, y+25), "Invoice Date: 15 March 2024", fill="#111", font=None)
    draw.text((40, y+50), "Due Date:     30 March 2024", fill="#111", font=None)

    draw.text((450, y), "Bill To:", fill="#555", font=None)
    draw.text((450, y+25), "Infosys Limited", fill="#111", font=None)
    draw.text((450, y+50), "GSTIN: 29AABCI1234A1Z4", fill="#111", font=None)
    draw.text((450, y+75), "Bengaluru - 560100, KA", fill="#111", font=None)

    # Line items header
    y = 280
    draw.rectangle([30, y, 770, y+30], fill="#e3f2fd")
    draw.text((40, y+7), "Description", fill="#333", font=None)
    draw.text((380, y+7), "Qty", fill="#333", font=None)
    draw.text((450, y+7), "Unit Price", fill="#333", font=None)
    draw.text((620, y+7), "Amount", fill="#333", font=None)

    items = [
        ("Dell Laptop XPS 15 (Core i7, 16GB RAM)", "2", "₹85,000", "₹1,70,000"),
        ("HP LaserJet Pro M404n Printer", "3", "₹22,500", "₹67,500"),
        ("Logitech MX Keys Keyboard (Wireless)", "10", "₹5,500", "₹55,000"),
        ("LG 27\" 4K Monitor UltraFine", "4", "₹35,000", "₹1,40,000"),
        ("Annual Software License – MS Office 365", "15", "₹6,200", "₹93,000"),
    ]

    y = 320
    for desc, qty, unit, amt in items:
        draw.text((40, y), desc[:50], fill="#111", font=None)
        draw.text((380, y), qty, fill="#111", font=None)
        draw.text((450, y), unit, fill="#111", font=None)
        draw.text((620, y), amt, fill="#111", font=None)
        y += 28
        draw.line([30, y-2, 770, y-2], fill="#e0e0e0", width=1)

    # Totals
    y += 20
    draw.line([400, y, 770, y], fill="#bbb", width=1); y += 10
    draw.text((420, y), "Subtotal:", fill="#555"); draw.text((620, y), "₹5,25,500", fill="#111")
    y += 25
    draw.text((420, y), "CGST @ 9%:", fill="#555"); draw.text((620, y), "₹47,295", fill="#111")
    y += 25
    draw.text((420, y), "SGST @ 9%:", fill="#555"); draw.text((620, y), "₹47,295", fill="#111")
    y += 25
    draw.rectangle([400, y, 770, y+35], fill="#1a237e")
    draw.text((420, y+9), "TOTAL AMOUNT:", fill="white"); draw.text((600, y+9), "₹6,20,090", fill="white")

    # Footer
    y += 70
    draw.text((40, y), "Bank: HDFC Bank  |  A/C: 50200067890123  |  IFSC: HDFC0001234", fill="#555")
    y += 25
    draw.text((40, y), "Terms: Payment due within 15 days. Late fee 2% per month.", fill="#777")
    y += 50
    draw.line([30, y, 770, y], fill="#bbb")
    draw.text((40, y+10), "Authorised Signatory – TECHMART SOLUTIONS PVT LTD", fill="#333")

    img.save("sample_invoice.png")
    print("✅ sample_invoice.png created")

if __name__ == "__main__":
    make_invoice()
