"""
Base async repository pattern for SQLAlchemy 2.x models.

Provides standard CRUD database query abstractions.
Repositories isolate database queries from business logic in services.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


class BaseRepository[ModelType: Base]:
    """
    Generic async repository providing CRUD database abstractions.

    Subclassed by domain repositories (e.g. UserRepository, RoleRepository).
    """

    def __init__(self, model: type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        """Fetch a single record by primary key."""
        result = await self.db.execute(
            select(self.model).where(getattr(self.model, "id") == id)  # noqa: B009
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Fetch multiple records with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, *, obj_in: dict[str, Any] | Any) -> ModelType:
        """Create and persist a new record."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        elif hasattr(obj_in, "model_dump"):
            create_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, "dict"):
            create_data = obj_in.dict(exclude_unset=True)
        else:
            create_data = vars(obj_in)

        db_obj = self.model(**create_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, *, db_obj: ModelType, obj_in: dict[str, Any] | Any
    ) -> ModelType:
        """Update an existing persistent record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        elif hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, "dict"):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = vars(obj_in)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, *, id: Any) -> ModelType | None:
        """Delete a record by primary key."""
        obj = await self.get(id)
        if obj is not None:
            await self.db.delete(obj)
            await self.db.commit()
        return obj

    async def count(self) -> int:
        """Return total count of records."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        count_val = result.scalar()
        return count_val if count_val is not None else 0
