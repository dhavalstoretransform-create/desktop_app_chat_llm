"""
API endpoints for managing Permissions.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DatabaseDep, require_permission
from app.models.user import User
from app.repositories.permission import PermissionRepository
from app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from app.services.permission import PermissionService

router = APIRouter()


@router.post("/", response_model=PermissionResponse, status_code=201)
async def create_permission(
    *,
    db: DatabaseDep,
    permission_in: PermissionCreate,
    current_user: Annotated[User, Depends(require_permission("permission.create"))],
) -> Any:
    """Create a new permission in the system."""
    repository = PermissionRepository(db)
    service = PermissionService(repository)
    try:
        return await service.create(obj_in=permission_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/", response_model=list[PermissionResponse])
async def list_permissions(
    *,
    db: DatabaseDep,
    current_user: Annotated[User, Depends(require_permission("permission.read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all permissions (paginated)."""
    repository = PermissionRepository(db)
    service = PermissionService(repository)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=PermissionResponse)
async def get_permission(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_permission("permission.read"))],
) -> Any:
    """Get a specific permission's details by UUID."""
    repository = PermissionRepository(db)
    service = PermissionService(repository)
    permission = await service.get(id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")
    return permission


@router.patch("/{id}", response_model=PermissionResponse)
async def update_permission(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    permission_in: PermissionUpdate,
    current_user: Annotated[User, Depends(require_permission("permission.update"))],
) -> Any:
    """Update an existing permission's information."""
    repository = PermissionRepository(db)
    service = PermissionService(repository)
    permission = await service.get(id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")
    try:
        update_dict = permission_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=PermissionResponse)
async def delete_permission(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_permission("permission.deactivate"))],
) -> Any:
    """Soft delete a permission by setting is_active to False."""
    repository = PermissionRepository(db)
    service = PermissionService(repository)
    permission = await service.get(id=id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found.")
    return await service.update(id=id, obj_in={"is_active": False})
