"""
API v1 router.

Each feature module registers its sub-router here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    ai_models,
    ai_providers,
    auth,
    dashboard,
    departments,
    health,
    permissions,
    roles,
    users,
    chat,
    conversations,
)

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_v1_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_v1_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_v1_router.include_router(ai_providers.router, prefix="/ai-providers", tags=["AI Providers"])
api_v1_router.include_router(ai_models.router, prefix="/ai-models", tags=["AI Models"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_v1_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
