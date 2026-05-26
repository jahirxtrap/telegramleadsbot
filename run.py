"""Uvicorn server launcher. Use --production for no-reload multi-worker mode."""

import os
import sys

import uvicorn


def main():
    is_production = "--production" in sys.argv
    port = int(os.environ.get("PORT", "8000"))
    workers = int(os.environ.get("WEB_CONCURRENCY", "2")) if is_production else 1

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,
        workers=workers,
    )


if __name__ == "__main__":
    main()
