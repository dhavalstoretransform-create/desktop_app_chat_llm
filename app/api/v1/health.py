"""
Health check router.

GET /health          → {"status": "ok"}
GET /api/v1/health   → {"status": "ok"}

This endpoint is unauthenticated.
It must not contain business logic or database calls.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.constants import HEALTH_STATUS_OK

router = APIRouter()


@router.get("/health", summary="Health check", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": HEALTH_STATUS_OK}
