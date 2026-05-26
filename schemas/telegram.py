"""Pydantic models for the subset of the Telegram Bot API we consume.

We only model the fields the bot reads. `extra="ignore"` lets Telegram add
fields without breaking validation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TelegramUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    is_bot: bool = False
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None


class TelegramChat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    type: str | None = None


class TelegramContact(BaseModel):
    model_config = ConfigDict(extra="ignore")

    phone_number: str
    first_name: str | None = None
    last_name: str | None = None
    user_id: int | None = None


class TelegramMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    message_id: int
    date: int | None = None
    text: str | None = None
    from_user: TelegramUser | None = Field(default=None, alias="from")
    chat: TelegramChat
    contact: TelegramContact | None = None


class TelegramUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    update_id: int
    message: TelegramMessage | None = None
    edited_message: TelegramMessage | None = None
