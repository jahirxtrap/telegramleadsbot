"""Telegram webhook receiver.

Telegram POSTs each update here. We verify the secret header, ack with 200
immediately, and process the message in the background so Telegram never
times out and retries.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Header, Request
from loguru import logger
from pydantic import ValidationError

from core.config import TELEGRAM_WEBHOOK_SECRET
from core.responses import api_response
from schemas.telegram import TelegramMessage, TelegramUpdate
from services import leads, telegram

router = APIRouter(tags=["Telegram"])


async def _process(message: TelegramMessage) -> None:
    reply = await leads.handle_message(message)
    if reply:
        await telegram.send_message(message.chat.id, reply)


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    background: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    # Constant-ish check: reject anyone who doesn't echo our secret token.
    if x_telegram_bot_api_secret_token != TELEGRAM_WEBHOOK_SECRET:
        return api_response(status=403)

    try:
        update = TelegramUpdate.model_validate(await request.json())
    except (ValidationError, ValueError) as exc:
        # Ack with 200 anyway so Telegram doesn't retry a malformed update.
        logger.warning("Discarding unparseable update: {}", exc)
        return api_response()

    message = update.message or update.edited_message
    if message is not None:
        background.add_task(_process, message)

    return api_response()
