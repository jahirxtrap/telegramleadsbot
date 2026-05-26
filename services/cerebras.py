"""Cerebras inference client (OpenAI-compatible Chat Completions API).

Docs: https://inference-docs.cerebras.ai — the endpoint mirrors OpenAI's
`/v1/chat/completions`. We use raw httpx to avoid an extra SDK dependency.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from loguru import logger

from core.config import CEREBRAS_API_KEY, CEREBRAS_BASE_URL, CEREBRAS_MODEL

_TIMEOUT = httpx.Timeout(30.0)
_MAX_RETRIES = 2          # extra attempts after the first
_BACKOFF_SECONDS = 1.5    # multiplied by the attempt number
_RETRY_STATUSES = {429, 500, 502, 503, 504}

Message = dict[str, str]


async def _completion(payload: dict[str, Any]) -> dict[str, Any]:
    if not CEREBRAS_API_KEY:
        logger.warning("CEREBRAS_API_KEY is empty — skipping Cerebras call")
        return {}
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{CEREBRAS_BASE_URL}/chat/completions"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for attempt in range(_MAX_RETRIES + 1):
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in _RETRY_STATUSES and attempt < _MAX_RETRIES:
                wait = _BACKOFF_SECONDS * (attempt + 1)
                logger.warning(
                    "Cerebras {} (attempt {}/{}), retrying in {}s",
                    resp.status_code, attempt + 1, _MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
    return {}


async def chat(
    messages: list[Message],
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 512,
) -> str:
    """Return the assistant's reply text, or "" on failure."""
    try:
        data = await _completion(
            {
                "model": model or CEREBRAS_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        logger.error("Cerebras chat failed: {}", exc)
        return ""


async def chat_json(
    messages: list[Message],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> dict[str, Any]:
    """Request a JSON object response and parse it. Returns {} on failure."""
    try:
        data = await _completion(
            {
                "model": model or CEREBRAS_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }
        )
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return json.loads(content) if content else {}
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
        logger.error("Cerebras chat_json failed: {}", exc)
        return {}
