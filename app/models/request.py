"""
TokenRequest ORM mapping.

Manages the lifecycle of token allocation requests.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TokenRequest(BaseModel):
    """ORM model representing a request for additional tokens."""

    __tablename__ = "token_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_token_wallets.id"),
        nullable=False,
    )
    requested_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    approved_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    request_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    request_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    admin_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
