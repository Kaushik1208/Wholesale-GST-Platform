# 🏪 GenAI Invoice & GST Intelligence Platform

A production-ready Streamlit app for wholesale businesses — upload invoices, let AI extract fields, track GST, and generate financial reports.

## ✨ Features
- EasyOCR + Groq (Llama 3.3 70B) for invoice parsing
- GST dashboard with ITC calculations
- Purchase & Sales ledger
- Invoice Q&A chatbot
- CSV export
- Flagged invoice detection

---

## 🚀 Deploy to Streamlit Cloud (Free, Permanent URL)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repo → branch: `main` → file: `app.py`
4. Click **Advanced settings → Secrets** and paste:
```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```
5. Click **Deploy** — your app will be live at:
   `https://your-username-your-repo-app-XXXX.streamlit.app`

That URL works **24/7**, shareable with anyone, no login needed.

---

## 💻 Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=gsk_...

# 3. Run
streamlit run app.py
```

Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys)

---

## 🏗️ Project Structure
```
invoice_platform/
├── app.py                   # Main app + navigation
├── utils/
│   ├── config.py            # API key loader (secrets/env)
│   ├── gemini_utils.py      # Groq LLM helpers
│   ├── ocr_utils.py         # EasyOCR / PDF text extraction
│   ├── db.py                # SQLite persistence
│   ├── validators.py        # GST/invoice validation
│   └── csv_export.py        # CSV download helper
├── pages/
│   ├── gst_dashboard.py     # Financial overview + ITC
│   ├── upload_page.py       # Upload + AI pipeline
│   ├── purchase_page.py     # Purchase ledger
│   ├── sales_page.py        # Sales ledger
│   ├── ledger_page.py       # Combined GST ledger
│   ├── qa_page.py           # Invoice Q&A chatbot
│   └── history_page.py      # Invoice history
├── assets/style.css         # Dark theme CSS
├── .streamlit/
│   ├── config.toml          # Theme config
│   └── secrets.toml         # ← DO NOT commit, add on Streamlit Cloud
└── requirements.txt
```
