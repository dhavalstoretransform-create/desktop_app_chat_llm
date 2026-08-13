"""
AI Provider repository for database access.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_provider import AIProvider
from app.repositories.base import BaseRepository


class AIProviderRepository(BaseRepository[AIProvider]):
    """Repository handling database operations for AI Providers."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=AIProvider, db=db)

    async def get_by_code(self, code: str) -> AIProvider | None:
        """Fetch an AI Provider by its unique stable code."""
        query = select(self.model).where(self.model.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
