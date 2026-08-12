"""
AI Model ORM mapping.

Defines the structure for storing configuration, pricing, and availability
metadata for registered LLM models.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.ai_provider import AIProvider


class AIModel(BaseModel):
    """ORM model representing an approved AI model.
    
    Pricing fields represent prices normalized per 1,000,000 (one million) tokens.
    """

    __tablename__ = "ai_models"

    __table_args__ = (
        UniqueConstraint(
            "provider_id", "code", name="uq_ai_models_provider_id_code"
        ),
        CheckConstraint(
            "input_token_price >= 0",
            name="check_input_token_price_non_negative",
        ),
        CheckConstraint(
            "output_token_price >= 0",
            name="check_output_token_price_non_negative",
        ),
        CheckConstraint(
            "max_context_tokens > 0",
            name="check_max_context_tokens_positive",
        ),
        CheckConstraint(
            "max_output_tokens > 0",
            name="check_max_output_tokens_positive",
        ),
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_providers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    input_token_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    output_token_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        default=Decimal("0.0000"),
    )
    max_context_tokens: Mapped[int] = mapped_column(
        nullable=False,
        default=4096,
    )
    max_output_tokens: Mapped[int] = mapped_column(
        nullable=False,
        default=2048,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Relationship back to Provider
    provider: Mapped[AIProvider] = relationship(
        "AIProvider",
        back_populates="models",
        lazy="select",
    )
