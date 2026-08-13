"""
Junction table for many-to-many relationship between roles and permissions.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Table

from app.core.database import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    ),
    Column(
        "permission_id",
        ForeignKey("permissions.id", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    ),
)

