#  Wabi Sabi Executioner

AI-powered SEO Master Plan Generator. Built with FastAPI + Claude 3.5 + Firecrawl + Google Sheets.

---

##  Project Structure

```
wabisabi/
├── main.py                   # FastAPI app & routes
├── config.py                 # Settings from .env
├── requirements.txt          # Python dependencies
├── .env                      # ← YOUR API KEYS GO HERE
├── credentials.json          # ← Google Service Account JSON
├── services/
│   ├── claude_service.py     # Dual parallel Claude API calls
│   ├── firecrawl_service.py  # Competitor URL scraping
│   ├── sheets_service.py     # Google Sheets save/load
│   └── indexnow_service.py   # IndexNow API ping
├── templates/
│   ├── index.html            # Main generation UI
│   └── clients.html          # Client registry page
└── static/                   # CSS/JS assets
```

---

##  Setup

### 1. Prerequisites
- Python 3.11+ (3.14 compatible)
- pip

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Edit the `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-...
FIRECRAWL_API_KEY=fc-...
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
INDEXNOW_KEY=your-random-key-string
AGENCY_NAME=Wabi Sabi Agency
```

### 4. Google Sheets Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project → Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → Download JSON → save as `credentials.json` in project root
4. Create a Google Sheet → Share it with the service account email
5. Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### 5. IndexNow Key
Just make up any random alphanumeric string (e.g., `a3f7b2d9e1c4`). No signup needed.
You'd host a `your-key.txt` file on the client domain for verification — for now it just pings the API.

### 6. Run the app
```bash
python main.py
```
Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open: **http://localhost:8000**

---

##  What Gets Generated (7 files in 1 ZIP)

| File | Description |
|---|---|
| `deep-schema.json` | Full JSON-LD schema.org markup (Organization, WebSite, FAQ, etc.) |
| `rag-architecture.html` | RAG content architecture recommendations |
| `semantic-tables.html` | Competitor comparison tables |
| `ai-training-faq.csv` | 20 targeted Q&As from audience brain-dump |
| `llms-full.txt` | LLM-optimized content brief with date stamp |
| `client-facing-report.md` | Polished client report with 90-day roadmap |
| `press-release-draft.md` | AP-style press release (DRAFT ONLY warning hardcoded) |

---

##  How It Works

1. **Firecrawl** scrapes client URL + up to 3 competitor URLs
2. **Two parallel Claude 3.5 Sonnet calls** generate all 7 files simultaneously (avoids token timeouts)
3. Files are **zipped** and returned as a download
4. **IndexNow API** is pinged with the client URL
5. Config is **saved to Google Sheets** for the client registry

---

##  Safety Features
- All invented facts are tagged `[CLIENT VERIFICATION REQUIRED]`
- Press release always has `*** DRAFT ONLY: REQUIRES FOUNDER REVIEW ***` at the top
- Attribution is opt-in via toggle

---

##  API Keys Summary

| Key | Where to get |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `FIRECRAWL_API_KEY` | [firecrawl.dev](https://firecrawl.dev) |
| `credentials.json` | Google Cloud Console → Service Accounts |
| `GOOGLE_SHEET_ID` | From your Google Sheet URL |
| `INDEXNOW_KEY` | Self-generated random string |
