"""
API endpoints for managing User Roles.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DatabaseDep
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.role import RoleService

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    *,
    db: DatabaseDep,
    role_in: RoleCreate,
) -> Any:
    """Create a new user role in the system."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    try:
        return await service.create(obj_in=role_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None



@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    *,
    db: DatabaseDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all user roles (paginated)."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=RoleResponse)
async def get_role(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
) -> Any:
    """Get a specific role's details by UUID."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    role = await service.get(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return role


@router.put("/{id}", response_model=RoleResponse)
async def update_role(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    role_in: RoleUpdate,
) -> Any:
    """Update an existing role's information."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    role = await service.get(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    try:
        update_dict = role_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None



@router.delete("/{id}", response_model=RoleResponse)
async def delete_role(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
) -> Any:
    """Soft delete a role by setting is_active to False."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    role = await service.get(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return await service.update(id=id, obj_in={"is_active": False})
