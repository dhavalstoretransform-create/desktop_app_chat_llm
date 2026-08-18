"""
TokenTransaction ORM mapping.

Records deductions and additions to the EmployeeTokenWallet.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TokenTransaction(BaseModel):
    """ORM model representing a token transaction for a user."""

    __tablename__ = "token_transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id"),
        nullable=True,
    )
    model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        nullable=True,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False, # e.g. "CHAT_COMPLETION", "REFUND", "TOPUP"
    )
    transaction_action: Mapped[str] = mapped_column(
        String(20),
        nullable=False, # "DEBIT" or "CREDIT"
    )
    tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
