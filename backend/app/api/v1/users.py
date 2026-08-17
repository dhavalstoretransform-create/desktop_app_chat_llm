"""
API endpoints for managing Users / Employees.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DatabaseDep, require_roles
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserListResponse
from app.services.user import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    *,
    db: DatabaseDep,
    user_in: UserCreate,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER"))],
) -> Any:
    """Create a new user/employee in the system."""
    repository = UserRepository(db)
    service = UserService(repository)
    try:
        user = await service.create(obj_in=user_in, current_user=current_user)
        return await repository.get(user.id)
    except ValueError as e:
        error_msg = str(e)
        if "does not exist" in error_msg and "Role" in error_msg:
            raise HTTPException(status_code=404, detail="Role not found.")
        if "already exists" in error_msg:
            from fastapi import status
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg) from None
        raise HTTPException(status_code=400, detail=error_msg) from None


@router.get("/", response_model=UserListResponse)
async def list_users(
    *,
    db: DatabaseDep,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "EMPLOYEE", "VIEWER"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all users (paginated)."""
    repository = UserRepository(db)
    service = UserService(repository)
    items = await service.get_multi(skip=skip, limit=limit)
    total = await repository.count()
    return {"items": items, "total": total}


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "EMPLOYEE", "VIEWER"))],
) -> Any:
    """Get a specific user's details by UUID."""
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER"))],
) -> Any:
    """Update an existing user's information."""
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        update_dict = user_in.model_dump(exclude_unset=True)
        
        # Check permissions for is_verified modification
        if "is_verified" in update_dict:
            if not current_user.role or current_user.role.code not in ["SUPER_ADMIN", "ADMIN"]:
                raise HTTPException(
                    status_code=403, 
                    detail="You do not have permission to verify or unverify users."
                )

        old_is_verified = user.is_verified
        old_role_id = user.role_id
        
        # Perform update
        updated_user = await service.update(id=id, obj_in=update_dict, current_user=current_user)
        
        from app.repositories.audit_log import AuditLogRepository
        audit_repo = AuditLogRepository(db)
        
        # Create audit log if is_verified was changed
        if "is_verified" in update_dict and update_dict["is_verified"] != old_is_verified:
            action = "USER_VERIFIED" if update_dict["is_verified"] else "USER_UNVERIFIED"
            await audit_repo.create(
                obj_in={
                    "user_id": current_user.id,
                    "action": action,
                    "entity_name": "user",
                    "entity_id": updated_user.id,
                    "description": f"User {updated_user.email} verification status changed to {update_dict['is_verified']} by {current_user.email}",
                }
            )
            
        # Create audit log if role_id was changed
        if "role_id" in update_dict and str(update_dict["role_id"]) != str(old_role_id):
            await audit_repo.create(
                obj_in={
                    "user_id": current_user.id,
                    "action": "ROLE_CHANGED",
                    "entity_name": "user",
                    "entity_id": updated_user.id,
                    "description": f"User {updated_user.email} role changed by {current_user.email}",
                }
            )
            
        # Ensure relationships are loaded for the response
        return await repository.get(updated_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=UserResponse)
async def delete_user(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles("SUPER_ADMIN", "ADMIN"))],
) -> Any:
    """Soft delete a user by setting is_active to False."""
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return await service.update(id=id, obj_in={"is_active": False})
