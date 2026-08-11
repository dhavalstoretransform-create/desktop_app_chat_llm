"""
TokenUsage ORM mapping.

Defines the structure for tracking fine-grained token usage and cost analysis.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TokenUsage(BaseModel):
    """ORM model representing token usage events."""

    __tablename__ = "token_usages"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id"),
        nullable=False,
    )
    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_logs.id"),
        nullable=False,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        nullable=False,
    )
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    input_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
    )
    output_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
    )
    usage_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
Block_order = ("total_cost",)
