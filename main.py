"""TelegramLeadsBot — FastAPI application entry point."""

import importlib
import pkgutil

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded

from core.rate_limit import limiter
from core.responses import api_response
from middleware.error_handler import register_error_handlers
from middleware.security import register_security_middleware
import routers as routers_pkg


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="TelegramLeadsBot API",
    version="0.1.0",
    description="Capture Telegram leads into Google Sheets, assisted by Cerebras",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return api_response(status=429)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

register_security_middleware(app)
register_error_handlers(app)

for module_info in pkgutil.iter_modules(routers_pkg.__path__):
    module = importlib.import_module(f"routers.{module_info.name}")
    if hasattr(module, "router"):
        app.include_router(module.router, prefix="/api")


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
    include_in_schema=False,
)
async def catch_all(request: Request, path: str):
    return api_response(status=404)
