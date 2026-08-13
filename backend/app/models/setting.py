"""
SystemSetting ORM mapping.

Defines organizational configuration settings for the system.
"""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SystemSetting(BaseModel):
    """ORM model representing organizational settings configuration."""

    __tablename__ = "system_settings"

    setting_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    setting_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_editable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
