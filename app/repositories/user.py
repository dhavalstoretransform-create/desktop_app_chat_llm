"""
User repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for users."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=User, db=db)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a single user by their unique email."""
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_employee_code(self, employee_code: str) -> User | None:
        """Fetch a single user by their unique employee code."""
        query = select(self.model).where(self.model.employee_code == employee_code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
