"""
Role service encapsulating business rules for roles.
"""

from __future__ import annotations

from typing import Any

from app.models.role import Role
from app.repositories.role import RoleRepository
from app.services.base import BaseService


class RoleService(BaseService[Role, RoleRepository]):
    """Service class handling role management operations."""

    def __init__(self, repository: RoleRepository) -> None:
        super().__init__(repository=repository)

    async def create(self, *, obj_in: dict[str, Any] | Any) -> Role:
        """Create a role, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing:
                raise ValueError(f"Role with code '{code}' already exists.")
        return await super().create(obj_in=obj_in)

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any
    ) -> Role | None:
        """Update a role, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing and existing.id != id:
                raise ValueError(f"Role with code '{code}' already exists.")
        return await super().update(id=id, obj_in=obj_in)


