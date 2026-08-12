"""
User ORM mapping.

Defines the structure for employees and administrators in the system.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.role import Role


class User(BaseModel):
    """ORM model representing a system user."""

    __tablename__ = "users"

    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id"),
        nullable=False,
        index=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    role: Mapped[Role] = relationship("Role", lazy="select")
    department: Mapped[Department] = relationship("Department", lazy="select")


