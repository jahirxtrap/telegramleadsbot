"""Health endpoint — keeps the service alive and pingable."""

from fastapi import APIRouter

from core.responses import api_response

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return api_response()
