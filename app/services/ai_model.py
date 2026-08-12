"""
AI Model service encapsulating business rules for LLM models.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.models.ai_model import AIModel
from app.repositories.ai_model import AIModelRepository
from app.services.base import BaseService


class AIModelService(BaseService[AIModel, AIModelRepository]):
    """Service class handling AI Model operations."""

    def __init__(self, repository: AIModelRepository) -> None:
        super().__init__(repository=repository)

    async def get_multi_by_provider(
        self, *, provider_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
    ) -> list[AIModel]:
        """Fetch multiple AI Models with optional provider filtering."""
        return await self.repository.get_multi_by_provider(
            provider_id=provider_id, skip=skip, limit=limit
        )

    async def create(self, *, obj_in: dict[str, Any] | Any) -> AIModel:
        """Create an AI Model, enforcing code uniqueness per provider."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        provider_id = (
            obj_in.get("provider_id")
            if is_dict
            else getattr(obj_in, "provider_id", None)
        )
        if code and provider_id:
            existing = await self.repository.get_by_code_and_provider(
                code=code, provider_id=provider_id
            )
            if existing:
                raise ValueError(
                    f"AI Model with code '{code}' already exists "
                    f"under provider '{provider_id}'."
                )
        return await super().create(obj_in=obj_in)

    async def update(self, *, id: Any, obj_in: dict[str, Any] | Any) -> AIModel | None:
        """Update an AI Model, enforcing code uniqueness per provider."""
        current_model = await self.repository.get(id=id)
        if not current_model:
            return None

        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        provider_id = (
            obj_in.get("provider_id")
            if is_dict
            else getattr(obj_in, "provider_id", None)
        )

        # Fallback to current values if not provided in updates
        final_code = code or current_model.code
        final_provider_id = provider_id or current_model.provider_id

        if code or provider_id:
            existing = await self.repository.get_by_code_and_provider(
                code=final_code, provider_id=final_provider_id
            )
            if existing and existing.id != id:
                raise ValueError(
                    f"AI Model with code '{final_code}' already exists "
                    f"under provider '{final_provider_id}'."
                )
        return await super().update(id=id, obj_in=obj_in)
