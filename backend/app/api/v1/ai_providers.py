"""
API endpoints for managing AI Providers.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DatabaseDep, require_roles
from app.models.user import User
from app.repositories.ai_provider import AIProviderRepository
from app.schemas.ai_provider import (
    AIProviderCreate,
    AIProviderResponse,
    AIProviderUpdate,
)
from app.services.ai_provider import AIProviderService

router = APIRouter()


@router.post("/", response_model=AIProviderResponse, status_code=201)
async def create_provider(
    *,
    db: DatabaseDep,
    provider_in: AIProviderCreate,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER"))],
) -> Any:
    """Create a new AI Provider."""
    repository = AIProviderRepository(db)
    service = AIProviderService(repository)
    try:
        return await service.create(obj_in=provider_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/", response_model=list[AIProviderResponse])
async def list_providers(
    *,
    db: DatabaseDep,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "EMPLOYEE", "VIEWER"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all AI Providers (paginated)."""
    repository = AIProviderRepository(db)
    service = AIProviderService(repository)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=AIProviderResponse)
async def get_provider(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "EMPLOYEE", "VIEWER"))],
) -> Any:
    """Get details of a specific AI Provider."""
    repository = AIProviderRepository(db)
    service = AIProviderService(repository)
    provider = await service.get(id=id)
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found.")
    return provider


@router.patch("/{id}", response_model=AIProviderResponse)
async def update_provider(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    provider_in: AIProviderUpdate,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER"))],
) -> Any:
    """Partially update an existing AI Provider."""
    repository = AIProviderRepository(db)
    service = AIProviderService(repository)
    provider = await service.get(id=id)
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found.")
    try:
        update_dict = provider_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=AIProviderResponse)
async def delete_provider(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[
        User, Depends(require_roles("SUPER_ADMIN", "ADMIN"))
    ],
) -> Any:
    """Soft delete/deactivate an AI Provider."""
    repository = AIProviderRepository(db)
    service = AIProviderService(repository)
    provider = await service.get(id=id)
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found.")
    return await service.update(id=id, obj_in={"is_active": False})
