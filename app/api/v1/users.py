"""
API endpoints for managing Users / Employees.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DatabaseDep
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    *,
    db: DatabaseDep,
    user_in: UserCreate,
) -> Any:
    """Create a new user/employee in the system."""
    repository = UserRepository(db)
    service = UserService(repository)
    try:
        return await service.create(obj_in=user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/", response_model=list[UserResponse])
async def list_users(
    *,
    db: DatabaseDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all users (paginated)."""
    repository = UserRepository(db)
    service = UserService(repository)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
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
) -> Any:
    """Update an existing user's information."""
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        update_dict = user_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=UserResponse)
async def delete_user(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
) -> Any:
    """Soft delete a user by setting is_active to False."""
    repository = UserRepository(db)
    service = UserService(repository)
    user = await service.get(id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return await service.update(id=id, obj_in={"is_active": False})
