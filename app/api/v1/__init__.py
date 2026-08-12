"""
API v1 router.

Each feature module registers its sub-router here.
Phase 1: health only.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.ai_models import router as ai_models_router
from app.api.v1.ai_providers import router as ai_providers_router
from app.api.v1.departments import router as departments_router
from app.api.v1.health import router as health_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.roles import router as roles_router
from app.api.v1.users import router as users_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_v1_router.include_router(
    departments_router, prefix="/departments", tags=["departments"]
)
api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
api_v1_router.include_router(
    permissions_router, prefix="/permissions", tags=["permissions"]
)
api_v1_router.include_router(
    ai_providers_router, prefix="/ai-providers", tags=["ai-providers"]
)
api_v1_router.include_router(
    ai_models_router, prefix="/ai-models", tags=["ai-models"]
)




