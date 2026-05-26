"""Telegram Bot API client.

Thin async wrapper over https://api.telegram.org/bot<token>/<method>.
Only the methods the bot needs are implemented.
"""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from core.config import TELEGRAM_BOT_TOKEN

_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
_TIMEOUT = httpx.Timeout(15.0)


async def _call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST a Bot API method and return the parsed `result`, or {} on failure."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is empty — skipping Telegram call %s", method)
        return {}
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(f"{_API_BASE}/{method}", json=payload)
    data = resp.json()
    if not data.get("ok"):
        logger.error("Telegram {} failed: {}", method, data)
        return {}
    return data.get("result", {})


async def send_message(chat_id: int, text: str, parse_mode: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    return await _call("sendMessage", payload)


async def set_webhook(url: str, secret_token: str) -> dict[str, Any]:
    return await _call(
        "setWebhook",
        {
            "url": url,
            "secret_token": secret_token,
            "allowed_updates": ["message", "edited_message"],
            "drop_pending_updates": True,
        },
    )


async def delete_webhook() -> dict[str, Any]:
    return await _call("deleteWebhook", {"drop_pending_updates": False})


async def get_webhook_info() -> dict[str, Any]:
    return await _call("getWebhookInfo", {})
