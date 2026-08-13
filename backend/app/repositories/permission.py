"""
Permission repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository handling database operations for permissions."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Permission, db=db)

    async def get_by_code(self, code: str) -> Permission | None:
        """Fetch a single permission by its unique stable code."""
        query = select(self.model).where(self.model.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
