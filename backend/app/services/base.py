from typing import Any, cast

from app.core.database import Base
from app.repositories.base import BaseRepository


class BaseService[ModelType: Base, RepoType: BaseRepository[Any]]:
    """
    Generic service base class encapsulating business rules.

    Subclassed by domain services (e.g. UserService, TokenService).
    """

    def __init__(self, repository: RepoType) -> None:
        self.repository = repository

    async def get(self, id: Any) -> ModelType | None:
        """Get record by ID."""
        return cast(ModelType | None, await self.repository.get(id))

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        return cast(
            list[ModelType],
            # pyrefly: ignore [missing-attribute]
            await self.repository.get_multi(skip=skip, limit=limit),
        )

    async def create(self, *, obj_in: dict[str, Any] | Any) -> ModelType:
        """Create a new record."""
        return cast(ModelType, await self.repository.create(obj_in=obj_in))

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any
    ) -> ModelType | None:
        """Update an existing record by ID."""
        db_obj = await self.repository.get(id)
        if db_obj is None:
            return None
        return cast(
            ModelType, await self.repository.update(db_obj=db_obj, obj_in=obj_in)
        )

    async def delete(self, *, id: Any) -> ModelType | None:
        """Delete a record by ID."""
        return cast(ModelType | None, await self.repository.delete(id=id))

    async def count(self) -> int:
        """Get total count of records."""
        return await self.repository.count()


