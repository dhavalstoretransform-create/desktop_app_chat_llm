"""
Role repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository handling database operations for user roles."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=Role, db=db)

    async def get_by_name(self, name: str) -> Role | None:
        """Fetch a single role by its name."""
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Role | None:
        """Fetch a single role by its unique stable code."""
        query = select(self.model).where(self.model.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


