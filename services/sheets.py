"""Google Sheets integration via a deployed Apps Script web app.

The Apps Script `doPost(e)` receives the JSON below, checks `secret`, and
appends a row. See apps_script/Code.gs for the matching script.
"""

from __future__ import annotations

import asyncio

import httpx
from loguru import logger

from core.config import SHEETS_SHARED_SECRET, SHEETS_WEBAPP_URL
from schemas.lead import Lead

# Apps Script web apps answer with a 302 redirect to googleusercontent before
# returning the body, so we must follow redirects.
_TIMEOUT = httpx.Timeout(20.0)
_MAX_RETRIES = 2          # Apps Script 5xx errors are flaky/transient under concurrency
_BACKOFF_SECONDS = 1.5
_RETRY_STATUSES = {500, 502, 503, 504, 429}


async def append_lead(lead: Lead) -> bool:
    """Append a lead as a new row. Returns True on success."""
    if not SHEETS_WEBAPP_URL:
        logger.warning("SHEETS_WEBAPP_URL is empty — skipping Sheets append")
        return False

    body = {"secret": SHEETS_SHARED_SECRET, "lead": lead.model_dump()}
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            for attempt in range(_MAX_RETRIES + 1):
                resp = await client.post(SHEETS_WEBAPP_URL, json=body)
                if resp.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                    wait = _BACKOFF_SECONDS * (attempt + 1)
                    logger.warning(
                        "Sheets {} (attempt {}/{}), retrying in {}s",
                        resp.status_code, attempt + 1, _MAX_RETRIES, wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                break
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            logger.error("Sheets append rejected: {}", data)
            return False
        return True
    except (httpx.HTTPError, ValueError) as exc:
        logger.error("Sheets append failed: {}", exc)
        return False
