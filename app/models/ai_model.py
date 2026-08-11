"""
AI Model ORM mapping.

Defines the structure for storing configuration, pricing, and availability
metadata for registered LLM models.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AIModel(BaseModel):
    """ORM model representing an approved AI model."""

    __tablename__ = "ai_models"

    model_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    model_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    max_context_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    input_cost_per_million: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    output_cost_per_million: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
