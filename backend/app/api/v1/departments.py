"""
API endpoints for managing Organization Departments.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import DatabaseDep, require_permission
from app.models.user import User
from app.repositories.department import DepartmentRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department import DepartmentService

router = APIRouter()


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    *,
    db: DatabaseDep,
    department_in: DepartmentCreate,
    current_user: Annotated[User, Depends(require_permission("department.create"))],
) -> Any:
    """Create a new department."""
    repository = DepartmentRepository(db)
    service = DepartmentService(repository)
    try:
        return await service.create(obj_in=department_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.get("/", response_model=list[DepartmentResponse])
async def list_departments(
    *,
    db: DatabaseDep,
    current_user: Annotated[User, Depends(require_permission("department.read"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Retrieve all departments (paginated)."""
    repository = DepartmentRepository(db)
    service = DepartmentService(repository)
    return await service.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=DepartmentResponse)
async def get_department(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_permission("department.read"))],
) -> Any:
    """Get a specific department's details by UUID."""
    repository = DepartmentRepository(db)
    service = DepartmentService(repository)
    department = await service.get(id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    return department


@router.patch("/{id}", response_model=DepartmentResponse)
async def update_department(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    department_in: DepartmentUpdate,
    current_user: Annotated[User, Depends(require_permission("department.update"))],
) -> Any:
    """Update an existing department."""
    repository = DepartmentRepository(db)
    service = DepartmentService(repository)
    department = await service.get(id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    try:
        update_dict = department_in.model_dump(exclude_unset=True)
        return await service.update(id=id, obj_in=update_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{id}", response_model=DepartmentResponse)
async def delete_department(
    *,
    db: DatabaseDep,
    id: uuid.UUID,
    current_user: Annotated[User, Depends(require_permission("department.deactivate"))],
) -> Any:
    """Soft delete a department by setting is_active to False."""
    repository = DepartmentRepository(db)
    service = DepartmentService(repository)
    department = await service.get(id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")
    return await service.update(id=id, obj_in={"is_active": False})
