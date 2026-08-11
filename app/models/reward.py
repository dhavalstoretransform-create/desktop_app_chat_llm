"""
PromptReward ORM mapping.

Tracks prompt reuse events and grants reward points to original authors.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PromptReward(BaseModel):
    """ORM model representing prompt reuse rewards."""

    __tablename__ = "prompt_rewards"

    original_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    reused_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    original_prompt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_logs.id"),
        nullable=False,
    )
    reused_prompt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_logs.id"),
        nullable=False,
    )
    similarity_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    reward_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
