"""Pydantic validation schemas package."""

from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

__all__ = [
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
]
