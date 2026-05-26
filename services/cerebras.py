"""Cerebras inference client (OpenAI-compatible Chat Completions API)."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

import httpx
from loguru import logger

from core.config import CEREBRAS_API_KEY, CEREBRAS_BASE_URL, CEREBRAS_MODEL

_TIMEOUT = httpx.Timeout(30.0)
_MAX_RETRIES = 2
_BACKOFF_SECONDS = 1.5
_RETRY_STATUSES = {429, 500, 502, 503, 504}

Message = dict[str, str]


async def _completion(payload: dict[str, Any]) -> dict[str, Any]:
    if not CEREBRAS_API_KEY:
        logger.warning("CEREBRAS_API_KEY is empty, skipping Cerebras call")
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
                await asyncio.sleep(_BACKOFF_SECONDS * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json()
    return {}


def _extract_json(content: str) -> dict[str, Any]:
    if not content:
        return {}
    text = content.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return {}
    try:
        parsed = json.loads(text[start : end + 1])
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


async def chat(
    messages: list[Message],
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 512,
) -> str:
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
        return _extract_json(content)
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        logger.error("Cerebras chat_json failed: {}", exc)
        return {}
