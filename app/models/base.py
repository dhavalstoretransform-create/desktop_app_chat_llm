"""
Base ORM model declarations and mixins.

Uses SQLAlchemy 2.x Mapped and mapped_column syntax.
All timestamps are stored in UTC.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Mixin for UTC created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Abstract base model combining UUID primary key and UTC timestamps.

    All domain ORM models inherit from this class.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        fields = [f"id={self.id!r}"]
        if hasattr(self, "name"):
            fields.append(f"name={self.name!r}")
        return f"<{self.__class__.__name__}({', '.join(fields)})>"
