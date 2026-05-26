"""Lead qualification record. Field order mirrors the Google Sheet columns."""

from __future__ import annotations

from pydantic import BaseModel


class LeadRecord(BaseModel):
    date: str
    telegram_user: str | None = None
    received_text: str
    language: str | None = None
    sector: str | None = None
    employees: int | None = None
    location: str | None = None
    ai_interest: bool | None = None
    decision: str
    reason: str | None = None
