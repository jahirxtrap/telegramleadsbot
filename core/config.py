"""Application configuration.

All config comes from environment variables. For local dev a `.env` file at the
project root is auto-loaded (python-dotenv); in production (Render) the env vars
are injected by the platform and `.env` simply isn't present.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Public base URL of this service (used to register the Telegram webhook)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# Secret token Telegram echoes back in the X-Telegram-Bot-Api-Secret-Token header.
TELEGRAM_WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "dev-webhook-secret")

# Google Sheets (Apps Script web app endpoint)
SHEETS_WEBAPP_URL = os.environ.get("SHEETS_WEBAPP_URL", "")
# Shared secret sent in the POST body so the Apps Script can reject foreign requests.
SHEETS_SHARED_SECRET = os.environ.get("SHEETS_SHARED_SECRET", "dev-sheets-secret")

# Cerebras (OpenAI-compatible inference API)
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
