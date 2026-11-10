# Wabi Sabi Executioner

An AI-powered SEO master-plan generator. Given a client URL and up to three
competitor URLs, it scrapes the sites, runs two parallel Claude calls to produce
a full set of SEO deliverables, pings IndexNow, logs the run to Google Sheets,
and returns everything as a single ZIP.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Web framework | FastAPI, Uvicorn |
| Templating | Jinja2 |
| Content generation | Anthropic Claude (Sonnet 4) |
| Web scraping | Firecrawl |
| Client registry | Google Sheets (gspread) |
| Search notification | IndexNow |

---

## Project structure

```
WABI-SABI-EXECUTIONER/
├── main.py                     # FastAPI app and routes
├── config.py                   # Settings loaded from .env
├── requirements.txt
├── .env.example                # Environment template
├── services/
│   ├── claude_service.py       # Two parallel Claude calls -> 7 output files
│   ├── firecrawl_service.py    # Client and competitor scraping
│   ├── sheets_service.py       # Google Sheets save / load
│   └── indexnow_service.py     # IndexNow ping
└── templates/
    ├── index.html              # Main generation UI
    └── clients.html            # Client registry page
```

A `static/` directory is optional; it is mounted at `/static` only if present.

---

## Prerequisites

- Python 3.11 or newer
- An Anthropic API key and a Firecrawl API key
- A Google service account with the Sheets and Drive APIs enabled (for the
  client registry)

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/MuziSan07/WABI-SABI-EXECUTIONER.git
cd WABI-SABI-EXECUTIONER

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# then edit .env with your keys

# 5. Run
python main.py
```

The app runs at `http://localhost:8000` (configurable via `APP_HOST` / `APP_PORT`).

---

## Configuration

All settings are read from environment variables (via `.env`). See
`.env.example` for a template.

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key ([console.anthropic.com](https://console.anthropic.com)) |
| `FIRECRAWL_API_KEY` | Firecrawl API key ([firecrawl.dev](https://firecrawl.dev)) |
| `GOOGLE_CREDENTIALS_PATH` | Path to the Google service-account JSON (default `credentials.json`) |
| `GOOGLE_SHEET_ID` | Target Google Sheet ID, taken from its URL |
| `INDEXNOW_KEY` | A self-generated random key string |
| `AGENCY_NAME` | Agency name used for optional attribution |
| `APP_HOST` / `APP_PORT` | Bind address and port (default `0.0.0.0:8000`) |

### Google Sheets

1. In the [Google Cloud Console](https://console.cloud.google.com), create a
   project and enable the **Google Sheets API** and **Google Drive API**.
2. Create a **Service Account**, download its JSON key, and save it as
   `credentials.json` in the project root (git-ignored).
3. Create a Google Sheet and share it with the service-account email.
4. Copy the Sheet ID from the URL into `GOOGLE_SHEET_ID`.

---

## What gets generated

Each run returns a ZIP containing seven files plus a `MANIFEST.txt`:

| File | Description |
|------|-------------|
| `deep-schema.json` | JSON-LD schema.org markup (Organization, WebSite, FAQ, etc.) |
| `rag-architecture.html` | RAG content-architecture recommendations |
| `semantic-tables.html` | Client vs competitor comparison tables |
| `ai-training-faq.csv` | 20 targeted Q&As from the audience brief |
| `llms-full.txt` | LLM-optimized content brief, date-stamped |
| `client-facing-report.md` | Client report with a 90-day roadmap |
| `press-release-draft.md` | AP-style press release (always marked DRAFT) |

---

## How it works

1. **Firecrawl** scrapes the client URL and up to three competitor URLs.
2. **Two parallel Claude calls** generate the seven files at once (one for
   data/code files, one for text/markdown) to avoid timeouts.
3. The files are zipped and returned as a download.
4. **IndexNow** is pinged with the client URL.
5. The run is **saved to Google Sheets** for the client registry.

---

## Safety features

- Invented facts are tagged `[CLIENT VERIFICATION REQUIRED]` rather than
  presented as verified.
- The press release always begins with `*** DRAFT ONLY: REQUIRES FOUNDER REVIEW ***`.
- Agency attribution is opt-in via a toggle.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file
for details.
