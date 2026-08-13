"""
Department service encapsulating business rules for departments.
"""

from __future__ import annotations

from typing import Any

from app.models.department import Department
from app.repositories.department import DepartmentRepository
from app.services.base import BaseService


class DepartmentService(BaseService[Department, DepartmentRepository]):
    """Service class handling department management operations."""

    def __init__(self, repository: DepartmentRepository) -> None:
        super().__init__(repository=repository)

    async def create(self, *, obj_in: dict[str, Any] | Any) -> Department:
        """Create a department, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing:
                raise ValueError(f"Department with code '{code}' already exists.")
        return await super().create(obj_in=obj_in)

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any
    ) -> Department | None:
        """Update a department, enforcing code uniqueness checks."""
        is_dict = isinstance(obj_in, dict)
        code = obj_in.get("code") if is_dict else getattr(obj_in, "code", None)
        if code:
            existing = await self.repository.get_by_code(code)
            if existing and existing.id != id:
                raise ValueError(f"Department with code '{code}' already exists.")
        return await super().update(id=id, obj_in=obj_in)


