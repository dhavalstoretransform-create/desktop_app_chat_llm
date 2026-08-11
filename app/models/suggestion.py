"""
SuggestedPrompt ORM mapping.

Saves recommendations for optimizing repeated employee prompts.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SuggestedPrompt(BaseModel):
    """ORM model representing prompt improvement suggestions."""

    __tablename__ = "suggested_prompts"

    prompt_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_logs.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    original_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    suggested_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    similarity_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
