"""
Department repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Repository handling database operations for organization departments."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Department, db=db)

    async def get_by_name(self, name: str) -> Department | None:
        """Fetch a single department by its name."""
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Department | None:
        """Fetch a single department by its unique stable code."""
        query = select(self.model).where(self.model.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


