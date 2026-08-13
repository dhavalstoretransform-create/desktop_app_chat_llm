"""
API endpoints for managing User Roles.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import DatabaseDep, require_permission
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.repositories.role import RoleRepository
from app.schemas.permission import PermissionResponse, RolePermissionsResponse
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.role import RoleService

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    *,
    db: DatabaseDep,
    role_in: RoleCreate,
    current_user: Annotated[User, Depends(require_permission("role.create"))],
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
    current_user: Annotated[User, Depends(require_permission("role.read"))],
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
    current_user: Annotated[User, Depends(require_permission("role.read"))],
) -> Any:
    """Get a specific role's details by UUID."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    role = await service.get(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return role


@router.patch("/{id}", response_model=RoleResponse)
async def update_role(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    role_in: RoleUpdate,
    current_user: Annotated[User, Depends(require_permission("role.update"))],
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
    current_user: Annotated[User, Depends(require_permission("role.deactivate"))],
) -> Any:
    """Soft delete a role by setting is_active to False."""
    repository = RoleRepository(db)
    service = RoleService(repository)
    role = await service.get(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return await service.update(id=id, obj_in={"is_active": False})


@router.post("/{id}/permissions", response_model=list[PermissionResponse])
async def assign_role_permissions(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    permission_ids: list[uuid.UUID],
    current_user: Annotated[User, Depends(require_permission("permission.assign"))],
) -> Any:
    """Assign a list of permission IDs to a role."""
    query = select(Role).where(Role.id == id).options(selectinload(Role.permissions))
    res = await db.execute(query)
    role = res.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")

    if not permission_ids:
        raise HTTPException(
            status_code=400, detail="Permission IDs list cannot be empty."
        )

    # Fetch permissions and validate they all exist
    perm_query = select(Permission).where(Permission.id.in_(permission_ids))
    perm_res = await db.execute(perm_query)
    permissions = perm_res.scalars().all()

    fetched_ids = {p.id for p in permissions}
    for pid in permission_ids:
        if pid not in fetched_ids:
            raise HTTPException(
                status_code=404, detail=f"Permission not found: {pid}"
            )

    role.permissions = list(permissions)
    await db.commit()
    await db.refresh(role)
    return role.permissions


@router.get("/{id}/permissions", response_model=RolePermissionsResponse)
async def get_role_permissions(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_permission("role.read"))],
) -> Any:
    """List all permissions assigned to a role."""
    query = select(Role).where(Role.id == id).options(selectinload(Role.permissions))
    res = await db.execute(query)
    role = res.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    
    if not role.permissions:
        return {
            "message": "No permissions are assigned to this role.",
            "data": [],
        }
    return {
        "message": "Role permissions retrieved successfully.",
        "data": role.permissions,
    }


