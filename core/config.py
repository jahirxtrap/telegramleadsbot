"""Application configuration loaded from environment variables (.env for local dev)."""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "dev-webhook-secret")

SHEETS_WEBAPP_URL = os.environ.get("SHEETS_WEBAPP_URL", "")
SHEETS_SHARED_SECRET = os.environ.get("SHEETS_SHARED_SECRET", "dev-sheets-secret")

CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "")
CEREBRAS_BASE_URL = os.environ.get("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
CEREBRAS_MODEL = os.environ.get("CEREBRAS_MODEL", "llama3.1-8b")

__all__ = [
    "BACKEND_URL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_WEBHOOK_SECRET",
    "SHEETS_WEBAPP_URL",
    "SHEETS_SHARED_SECRET",
    "CEREBRAS_API_KEY",
    "CEREBRAS_BASE_URL",
    "CEREBRAS_MODEL",
]
