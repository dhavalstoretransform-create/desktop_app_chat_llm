"""
Role Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    """Base fields for User Roles."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[A-Z0-9_]+$",
        description="Unique stable code identifier for authorization check logic",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Human readable display name of the role",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the role's purpose"
    )


class RoleCreate(RoleBase):
    """Schema for creating a new Role."""

    pass


class RoleUpdate(BaseModel):
    """Schema for updating an existing Role."""

    code: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[A-Z0-9_]+$",
        description="Unique stable code identifier for authorization check logic",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Human readable display name of the role",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the role's purpose"
    )


class RoleResponse(RoleBase):
    """Schema for Role details in API responses."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
