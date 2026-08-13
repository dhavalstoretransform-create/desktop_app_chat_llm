"""
Employee Token Wallet ORM mapping.

Tracks available token allocations, carry forwards, and daily usage limits.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class EmployeeTokenWallet(BaseModel):
    """ORM model representing an employee's token wallet."""

    __tablename__ = "employee_token_wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    daily_token_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    carry_forward_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    bonus_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    available_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    total_tokens_used_today: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_reset_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )
