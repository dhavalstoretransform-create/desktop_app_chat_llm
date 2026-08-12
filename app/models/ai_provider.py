"""
AI Provider ORM mapping.

Defines the structure for LLM providers (e.g. OpenAI, Anthropic, Google).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.ai_model import AIModel


class AIProvider(BaseModel):
    """ORM model representing an AI LLM provider."""

    __tablename__ = "ai_providers"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # One-to-many relationship with AI Models
    models: Mapped[list[AIModel]] = relationship(
        "AIModel",
        back_populates="provider",
        lazy="select",
    )
