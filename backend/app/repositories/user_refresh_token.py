"""
UserRefreshToken repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_refresh_token import UserRefreshToken
from app.repositories.base import BaseRepository


class UserRefreshTokenRepository(BaseRepository[UserRefreshToken]):
    """Repository handling database operations for user refresh tokens."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=UserRefreshToken, db=db)

    async def get_by_token(self, token: str) -> UserRefreshToken | None:
        """Fetch a refresh token record by its hashed token string."""
        import hashlib
        hashed_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        query = select(self.model).where(self.model.token == hashed_token)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
