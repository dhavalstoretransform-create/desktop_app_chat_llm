"""
User repository for database access.
"""

from typing import Any

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

    async def get_with_permissions(self, user_id: Any) -> User | None:
        """Fetch user by ID, eager loading role and permissions."""
        from sqlalchemy.orm import selectinload

        from app.models.role import Role

        query = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(
                selectinload(self.model.role).selectinload(Role.permissions)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
