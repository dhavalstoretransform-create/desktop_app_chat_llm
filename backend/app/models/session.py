"""
Chat Session ORM mapping.

Groups conversations between employees and selected LLM models.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ChatSession(BaseModel):
    """ORM model representing a chat session."""

    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        nullable=False,
    )
    session_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    session_status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )
    total_messages: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
