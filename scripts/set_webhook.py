#!/usr/bin/env python3
"""
Register / inspect / remove the Telegram webhook.

Run from the project root so the package imports resolve:

    python scripts/set_webhook.py set      # point Telegram at BACKEND_URL/api/telegram/webhook
    python scripts/set_webhook.py info      # print current webhook info
    python scripts/set_webhook.py delete    # remove the webhook (back to long polling)

Reads BACKEND_URL, TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET from the
environment / .env via core.config.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import BACKEND_URL, TELEGRAM_WEBHOOK_SECRET  # noqa: E402
from services import telegram  # noqa: E402

WEBHOOK_PATH = "/api/telegram/webhook"


async def _run(command: str) -> None:
    if command == "set":
        url = BACKEND_URL.rstrip("/") + WEBHOOK_PATH
        result = await telegram.set_webhook(url, TELEGRAM_WEBHOOK_SECRET)
        print(f"setWebhook -> {url}")
        print(result or "  (failed — check TELEGRAM_BOT_TOKEN and logs)")
    elif command == "info":
        print(await telegram.get_webhook_info() or "  (failed)")
    elif command == "delete":
        print(await telegram.delete_webhook() or "  (failed)")
    else:
        print(__doc__)
        sys.exit(1)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "info"
    asyncio.run(_run(command))


if __name__ == "__main__":
    main()
