"""
Department Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    """Base fields for Departments."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[A-Z0-9_]+$",
        description="Unique stable code identifier of the department (e.g. FINANCE)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human readable display name of the department",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the department"
    )


class DepartmentCreate(DepartmentBase):
    """Schema for creating a new Department."""

    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating an existing Department."""

    code: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[A-Z0-9_]+$",
        description="Unique stable code identifier of the department (e.g. FINANCE)",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Human readable display name of the department",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the department"
    )


class DepartmentResponse(DepartmentBase):
    """Schema for Department details in API responses."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
