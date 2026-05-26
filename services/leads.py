"""Lead orchestration: Telegram message -> Cerebras qualification -> Sheets + reply.

This is the glue the webhook router calls. Keep router-side logic thin.
"""

from __future__ import annotations

from loguru import logger

from schemas.lead import Lead
from schemas.telegram import TelegramMessage
from services import cerebras, sheets

_SYSTEM_PROMPT = (
    "You are a sales lead-qualification assistant for an inbound Telegram bot. "
    "Reply in the SAME language as the contact's message. "
    "Respond with ONLY a single JSON object and nothing else — no markdown, no schema. "
    "Use EXACTLY these keys and no others: reply, intent, qualified, summary. "
    "Do not output schema keys such as \"type\" or \"properties\". "
    '"reply" = a short, friendly answer to send back to the lead. '
    '"intent" = a 2-4 word label of what they want. '
    '"qualified" = boolean, true if they show genuine buying/contact intent. '
    '"summary" = one sentence summarizing the lead for a sales rep, in English.'
)


def _full_name(message: TelegramMessage) -> str | None:
    user = message.from_user
    if user is None:
        return None
    parts = [p for p in (user.first_name, user.last_name) if p]
    return " ".join(parts) or None


async def _qualify(full_name: str | None, text: str) -> dict:
    user_content = f"Contact name: {full_name or 'unknown'}\nMessage: {text}"
    return await cerebras.chat_json(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
    )


async def handle_message(message: TelegramMessage) -> str | None:
    """Process one inbound message. Returns the reply text to send, or None."""
    user = message.from_user
    if user is None or user.is_bot:
        return None

    text = (message.text or "").strip()
    phone = message.contact.phone_number if message.contact else None
    full_name = _full_name(message)

    # /start onboarding — no lead row yet, just greet.
    if text.lower() == "/start":
        return "Hi! Tell me what you're looking for and I'll get you connected."

    if not text and not phone:
        return None

    qualification = await _qualify(full_name, text) if text else {}

    lead = Lead(
        telegram_user_id=user.id,
        chat_id=message.chat.id,
        username=user.username,
        full_name=full_name,
        phone=phone,
        message=text or None,
        intent=qualification.get("intent"),
        qualified=qualification.get("qualified"),
        summary=qualification.get("summary"),
    )

    if not await sheets.append_lead(lead):
        logger.warning("Lead from {} not stored in Sheets", user.id)

    return qualification.get("reply") or "Thanks! We've received your message and will be in touch shortly."
