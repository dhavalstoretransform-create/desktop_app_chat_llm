"""
User Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base fields for Users."""

    employee_code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[A-Z0-9_-]+$",
        description="Unique employee code identifier",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the employee",
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="Email address of the employee",
    )
    role_id: uuid.UUID = Field(
        ...,
        description="Associated Role UUID",
    )
    department_id: uuid.UUID = Field(
        ...,
        description="Associated Department UUID",
    )
    is_verified: bool = Field(
        default=False,
        description="Whether the user account email is verified",
    )


class UserCreate(UserBase):
    """Schema for creating a new User."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Plain text password",
    )


class UserUpdate(BaseModel):
    """Schema for updating an existing User."""

    full_name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Full name of the employee",
    )
    email: str | None = Field(
        None,
        min_length=5,
        max_length=255,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="Email address of the employee",
    )
    role_id: uuid.UUID | None = Field(
        None,
        description="Associated Role UUID",
    )
    department_id: uuid.UUID | None = Field(
        None,
        description="Associated Department UUID",
    )
    is_verified: bool | None = Field(
        None,
        description="Whether the user account email is verified",
    )
    is_active: bool | None = Field(
        None,
        description="Whether the user account is active",
    )
    password: str | None = Field(
        None,
        min_length=8,
        max_length=100,
        description="Plain text password",
    )


class UserResponse(UserBase):
    """Schema for User details in API responses."""

    id: uuid.UUID
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
