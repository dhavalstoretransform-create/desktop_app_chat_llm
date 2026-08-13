"""Database query repositories package."""

from app.repositories.base import BaseRepository
from app.repositories.department import DepartmentRepository
from app.repositories.role import RoleRepository

__all__ = ["BaseRepository", "DepartmentRepository", "RoleRepository"]
