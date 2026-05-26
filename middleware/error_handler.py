"""Global exception handlers — route every error through the standard envelope."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from loguru import logger

from core.responses import api_response


def register_error_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return api_response(message=str(exc.detail), status=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.info(f"Validation error on {request.url.path}: {exc.errors()}")
        return api_response(status=422)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled: {type(exc).__name__}: {exc}")
        return api_response(status=500)

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return api_response(status=404)
