"""Lead payload sent to Google Sheets."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Lead(BaseModel):
    """A single captured lead. Maps 1:1 to a row in the spreadsheet."""

    telegram_user_id: int
    chat_id: int
    username: str | None = None
    full_name: str | None = None
    phone: str | None = None
    message: str | None = None
    # AI-derived fields
    intent: str | None = None
    qualified: bool | None = None
    summary: str | None = None
    captured_at: str = Field(default_factory=_now_iso)
