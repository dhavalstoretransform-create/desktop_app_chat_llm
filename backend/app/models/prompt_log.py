"""
PromptLog ORM mapping.

Maintains records of all prompts and AI answers for analysis and auditability.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PromptLog(BaseModel):
    """ORM model representing an audit log of prompt processing."""

    __tablename__ = "prompt_logs"

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
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id"),
        nullable=False,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        nullable=False,
    )
    prompt_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    response_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    prompt_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
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
    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_repeated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    suggested_prompt_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="completed",
        nullable=False,
    )
Block_order = ("ix_prompt_logs_prompt_hash",)
