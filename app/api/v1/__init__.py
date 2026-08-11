"""
API v1 router.

Each feature module registers its sub-router here.
Phase 1: health only.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.departments import router as departments_router
from app.api.v1.health import router as health_router
from app.api.v1.roles import router as roles_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_v1_router.include_router(
    departments_router, prefix="/departments", tags=["departments"]
)


