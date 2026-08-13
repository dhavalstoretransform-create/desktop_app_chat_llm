"""
Permission Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    """Base fields for Permissions."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\.]+$",
        description="Unique stable machine-readable permission code identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human readable name of the permission",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of what this permission allows"
    )
    resource: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Resource object of this permission (e.g. user, role)",
    )
    action: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Action permitted on the resource (e.g. read, write)",
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a new Permission."""

    pass


class PermissionUpdate(BaseModel):
    """Schema for updating an existing Permission."""

    code: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\.]+$",
        description="Unique stable machine-readable permission code identifier",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Human readable name of the permission",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of what this permission allows"
    )
    resource: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Resource object of this permission (e.g. user, role)",
    )
    action: str | None = Field(
        None,
        min_length=1,
        max_length=50,
        description="Action permitted on the resource (e.g. read, write)",
    )
    is_active: bool | None = Field(
        None,
        description="Whether the permission is active",
    )


class PermissionResponse(PermissionBase):
    """Schema for Permission details in API responses."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RolePermissionsResponse(BaseModel):
    """Structured response schema for role permissions."""

    message: str
    data: list[PermissionResponse]

