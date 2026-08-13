"""
AI Provider Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIProviderBase(BaseModel):
    """Base fields for AI Providers."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\-]+$",
        description="Unique stable machine-readable provider code identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human readable name of the AI Provider",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the provider"
    )


class AIProviderCreate(AIProviderBase):
    """Schema for creating a new AI Provider."""

    pass


class AIProviderUpdate(BaseModel):
    """Schema for updating an existing AI Provider."""

    code: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\-]+$",
        description="Unique stable machine-readable provider code identifier",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Human readable name of the AI Provider",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the provider"
    )
    is_active: bool | None = Field(
        None,
        description="Whether the provider is active",
    )


class AIProviderResponse(AIProviderBase):
    """Schema for AI Provider details in API responses."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
