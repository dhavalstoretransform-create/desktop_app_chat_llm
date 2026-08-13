"""
AuditLog repository for database access.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository handling database operations for audit logs."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=AuditLog, db=db)
