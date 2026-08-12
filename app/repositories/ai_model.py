"""
AI Model repository for database access.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_model import AIModel
from app.repositories.base import BaseRepository


class AIModelRepository(BaseRepository[AIModel]):
    """Repository handling database operations for AI Models."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=AIModel, db=db)

    async def get_by_code_and_provider(
        self, code: str, provider_id: uuid.UUID
    ) -> AIModel | None:
        """Fetch an AI Model by its code and provider ID."""
        query = (
            select(self.model)
            .where(self.model.code == code)
            .where(self.model.provider_id == provider_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi_by_provider(
        self, *, provider_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
    ) -> list[AIModel]:
        """Fetch multiple AI Models with optional provider filtering."""
        query = select(self.model)
        if provider_id is not None:
            query = query.where(self.model.provider_id == provider_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
