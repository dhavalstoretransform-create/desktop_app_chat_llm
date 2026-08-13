"""
ModelRecommendation ORM mapping.

Recommends appropriate models based on user activity topic.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ModelRecommendation(BaseModel):
    """ORM model representing a model recommendation."""

    __tablename__ = "model_recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    recommended_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_models.id"),
        nullable=False,
    )
