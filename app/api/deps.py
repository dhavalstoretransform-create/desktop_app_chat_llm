"""
Shared API dependencies.

Provides FastAPI dependency injection functions for:
  - Database sessions (get_db, DatabaseDep)
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Typed dependency alias for database session injection in route handlers
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]

__all__ = ["DatabaseDep", "get_db"]
