"""
API endpoints for managing AI Models.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DatabaseDep
from app.repositories.ai_model import AIModelRepository
from app.repositories.ai_provider import AIProviderRepository
from app.schemas.ai_model import AIModelCreate, AIModelResponse, AIModelUpdate
from app.services.ai_model import AIModelService

router = APIRouter()


@router.post("/", response_model=AIModelResponse, status_code=201)
async def create_model(
    *,
    db: DatabaseDep,
    model_in: AIModelCreate,
) -> Any:
    """Register a new AI Model under a provider."""
    # First validate provider exists
    provider_repo = AIProviderRepository(db)
    provider = await provider_repo.get(id=model_in.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="AI Provider not found.")

    repository = AIModelRepository(db)
    service = AIModelService(repository)
    try:
        return await service.create(obj_in=model_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/", response_model=list[AIModelResponse])
async def list_models(
    *,
    db: DatabaseDep,
    provider_id: Annotated[uuid.UUID | None, Query()] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> Any:
    """Retrieve all AI Models (paginated)."""
    repository = AIModelRepository(db)
    service = AIModelService(repository)
    return await service.get_multi_by_provider(
        provider_id=provider_id, skip=skip, limit=limit
    )


@router.get("/{id}", response_model=AIModelResponse)
async def get_model(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
) -> Any:
    """Get details of a specific AI Model."""
    repository = AIModelRepository(db)
    service = AIModelService(repository)
    model = await service.get(id=id)
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found.")
    return model


@router.patch("/{id}", response_model=AIModelResponse)
async def update_model(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    model_in: AIModelUpdate,
) -> Any:
    """Partially update an existing AI Model."""
    repository = AIModelRepository(db)
    service = AIModelService(repository)
    model = await service.get(id=id)
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found.")

    if model_in.provider_id is not None:
        provider_repo = AIProviderRepository(db)
        provider = await provider_repo.get(id=model_in.provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="AI Provider not found.")

    try:
        update_dict = model_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=AIModelResponse)
async def delete_model(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
) -> Any:
    """Soft delete/deactivate an AI Model."""
    repository = AIModelRepository(db)
    service = AIModelService(repository)
    model = await service.get(id=id)
    if not model:
        raise HTTPException(status_code=404, detail="AI Model not found.")
    return await service.update(id=id, obj_in={"is_active": False})
