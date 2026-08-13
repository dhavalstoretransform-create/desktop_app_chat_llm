"""
Permission service encapsulating business rules for permissions.
"""

from __future__ import annotations

from typing import Any

from app.models.permission import Permission
from app.repositories.permission import PermissionRepository
from app.services.base import BaseService


class PermissionService(BaseService[Permission, PermissionRepository]):
    """Service class handling permission management operations."""

    def __init__(self, repository: PermissionRepository) -> None:
        super().__init__(repository=repository)

    async def create(self, *, obj_in: dict[str, Any] | Any) -> Permission:
        """Create a permission, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing:
                raise ValueError(f"Permission with code '{code}' already exists.")
        return await super().create(obj_in=obj_in)

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any
    ) -> Permission | None:
        """Update a permission, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing and existing.id != id:
                raise ValueError(f"Permission with code '{code}' already exists.")
        return await super().update(id=id, obj_in=obj_in)
