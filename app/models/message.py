"""
ChatMessage ORM mapping.

Stores individual messages exchanged within a chat session.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ChatMessage(BaseModel):
    """ORM model representing an individual message in a chat session."""

    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id"),
        nullable=False,
    )
    sender_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    message_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    message_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    message_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
