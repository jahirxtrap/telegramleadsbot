"""
Uvicorn server launcher.

Usage:
    python run.py                 # Development (reload=True, workers=1)
    python run.py --production    # Production (reload=False, workers=4)
"""

import os
import sys

import uvicorn


def main():
    is_production = "--production" in sys.argv
    port = int(os.environ.get("PORT", "8000"))  # Render injects $PORT
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
