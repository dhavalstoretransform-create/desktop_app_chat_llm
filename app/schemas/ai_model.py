"""
AI Model Pydantic schemas for request validation and response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AIModelBase(BaseModel):
    """Base fields for AI Models."""

    provider_id: uuid.UUID = Field(
        ...,
        description="Foreign key ID targeting the associated AI Provider",
    )
    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\-\.]+$",
        description="Unique stable machine-readable model code identifier",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human readable name of the AI Model",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the model"
    )
    input_token_price: Decimal = Field(
        Decimal("0.0000"),
        ge=Decimal("0.0000"),
        description="Price per token for inputs",
    )
    output_token_price: Decimal = Field(
        Decimal("0.0000"),
        ge=Decimal("0.0000"),
        description="Price per token for outputs",
    )
    max_context_tokens: int = Field(
        4096,
        gt=0,
        description="Maximum tokens allowed in full context",
    )
    max_output_tokens: int = Field(
        2048,
        gt=0,
        description="Maximum tokens allowed in model response",
    )


class AIModelCreate(AIModelBase):
    """Schema for registering a new AI Model."""

    pass


class AIModelUpdate(BaseModel):
    """Schema for updating an existing AI Model."""

    provider_id: uuid.UUID | None = Field(
        None,
        description="Foreign key ID targeting the associated AI Provider",
    )
    code: str | None = Field(
        None,
        min_length=2,
        max_length=50,
        pattern=r"^[a-z0-9_\-\.]+$",
        description="Unique stable machine-readable model code identifier",
    )
    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Human readable name of the AI Model",
    )
    description: str | None = Field(
        None, max_length=255, description="Description of the model"
    )
    input_token_price: Decimal | None = Field(
        None,
        ge=Decimal("0.0000"),
        description="Price per token for inputs",
    )
    output_token_price: Decimal | None = Field(
        None,
        ge=Decimal("0.0000"),
        description="Price per token for outputs",
    )
    max_context_tokens: int | None = Field(
        None,
        gt=0,
        description="Maximum tokens allowed in full context",
    )
    max_output_tokens: int | None = Field(
        None,
        gt=0,
        description="Maximum tokens allowed in model response",
    )
    is_active: bool | None = Field(
        None,
        description="Whether the model is active",
    )


class AIModelResponse(AIModelBase):
    """Schema for AI Model details in API responses."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
