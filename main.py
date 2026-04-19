"""
main.py — Wabi Sabi Executioner
FastAPI backend powering the full SEO content generation pipeline.
"""
import io
import zipfile
import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import APP_HOST, APP_PORT
from services.firecrawl_service import scrape_url, scrape_multiple
from services.claude_service import generate_all_files
from services.indexnow_service import ping_indexnow
from services.sheets_service import save_client, load_clients

app = FastAPI(title="Wabi Sabi Executioner", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ── Pages ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    clients = load_clients()
    return templates.TemplateResponse("clients.html", {"request": request, "clients": clients})


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.post("/api/generate")
async def generate(
    client_name: Annotated[str, Form()],
    client_url: Annotated[str, Form()],
    competitor_1: Annotated[str, Form()] = "",
    competitor_2: Annotated[str, Form()] = "",
    competitor_3: Annotated[str, Form()] = "",
    audience: Annotated[str, Form()] = "",
    wabisabi_attribution: Annotated[str, Form()] = "no",
):
    """Main generation endpoint. Scrapes, calls Claude (2 parallel), zips, returns ZIP."""
    attribution = wabisabi_attribution.lower() == "yes"
    competitor_urls = [u for u in [competitor_1, competitor_2, competitor_3] if u.strip()]

    try:
        # 1. Scrape client URL + competitors in parallel
        scrape_tasks = [scrape_url(client_url)]
        if competitor_urls:
            scrape_tasks.append(scrape_multiple(competitor_urls))

        results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

        client_scraped = results[0] if not isinstance(results[0], Exception) else {"content": "[SCRAPE FAILED]"}
        competitors_data = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else []

        client_content = client_scraped.get("content", "") if isinstance(client_scraped, dict) else ""

        # 2. Generate files via Claude (2 parallel calls)
        files = await generate_all_files(
            client_name=client_name,
            client_url=client_url,
            scraped_client=client_content,
            competitors=competitors_data if isinstance(competitors_data, list) else [],
            audience=audience,
            wabisabi_attribution=attribution,
        )

        # 3. Ping IndexNow
        indexnow_result = await ping_indexnow(client_url)

        # 4. Save to Google Sheets
        save_client({
            "client_name": client_name,
            "client_url": client_url,
            "competitor_1": competitor_1,
            "competitor_2": competitor_2,
            "competitor_3": competitor_3,
            "audience": audience,
            "wabisabi_attribution": attribution,
        })

        # 5. Package into ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
            # Add a generation manifest
            manifest = f"""WABI SABI EXECUTIONER — Generation Manifest
Generated: {datetime.utcnow().isoformat()} UTC
Client: {client_name}
Client URL: {client_url}
Competitor URLs: {', '.join(competitor_urls) or 'None'}
Attribution: {'Yes' if attribution else 'No'}
IndexNow Ping: {indexnow_result['message']}

FILES INCLUDED:
""" + "\n".join(f"  - {f}" for f in files)
            zf.writestr("MANIFEST.txt", manifest)
        zip_buffer.seek(0)

        safe_name = client_name.lower().replace(" ", "-")
        filename = f"wabisabi-{safe_name}-{datetime.utcnow().strftime('%Y%m%d')}.zip"

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clients")
async def api_clients():
    """Return all saved clients as JSON."""
    return JSONResponse(content=load_clients())


@app.post("/api/scrape-preview")
async def scrape_preview(url: Annotated[str, Form()]):
    """Quick preview scrape for the UI."""
    try:
        result = await scrape_url(url)
        preview = result.get("content", "")[:500]
        return {"success": True, "preview": preview, "title": result.get("title", "")}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
