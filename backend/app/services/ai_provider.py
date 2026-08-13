"""
AI Provider service encapsulating business rules for LLM providers.
"""

from __future__ import annotations

from typing import Any

from app.models.ai_provider import AIProvider
from app.repositories.ai_provider import AIProviderRepository
from app.services.base import BaseService


class AIProviderService(BaseService[AIProvider, AIProviderRepository]):
    """Service class handling AI Provider operations."""

    def __init__(self, repository: AIProviderRepository) -> None:
        super().__init__(repository=repository)

    async def create(self, *, obj_in: dict[str, Any] | Any) -> AIProvider:
        """Create an AI Provider, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing:
                raise ValueError(f"AI Provider with code '{code}' already exists.")
        return await super().create(obj_in=obj_in)

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any
    ) -> AIProvider | None:
        """Update an AI Provider, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing and existing.id != id:
                raise ValueError(f"AI Provider with code '{code}' already exists.")
        return await super().update(id=id, obj_in=obj_in)
