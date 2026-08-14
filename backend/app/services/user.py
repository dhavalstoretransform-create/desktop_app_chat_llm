"""
User service encapsulating business rules for users.
"""

from __future__ import annotations

from typing import Any

from app.models.user import User
from app.repositories.department import DepartmentRepository
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.services.base import BaseService
from app.utils.security import hash_password


class UserService(BaseService[User, UserRepository]):
    """Service class handling user management operations."""

    def __init__(self, repository: UserRepository) -> None:
        super().__init__(repository=repository)

    def _hash_password(self, password: str) -> str:
        """Hash user passwords securely using Argon2."""
        return hash_password(password)

    def _check_role_assignment(self, current_user: User | None, target_role_code: str) -> None:
        """Enforce the role assignment matrix."""
        if target_role_code == "SUPER_ADMIN":
            raise ValueError("Cannot assign SUPER_ADMIN role.")

        if current_user is None:
            if target_role_code != "EMPLOYEE":
                raise ValueError("Public registration can only assign EMPLOYEE role.")
            return

        if not current_user.role:
            raise ValueError("Current user has no role.")

        current_role = current_user.role.code

        if current_role == "SUPER_ADMIN":
            return
        elif current_role == "ADMIN":
            if target_role_code == "ADMIN":
                raise ValueError("ADMIN cannot assign ADMIN role.")
            return
        elif current_role == "MANAGER":
            if target_role_code in ["ADMIN", "MANAGER"]:
                raise ValueError(f"MANAGER cannot assign {target_role_code} role.")
            return

        raise ValueError("User does not have permission to assign roles.")

    async def create(
        self, *, obj_in: dict[str, Any] | Any, current_user: User | None = None
    ) -> User:
        """Create a user, validating email, employee_code, role, and department."""
        is_dict = isinstance(obj_in, dict)

        email = obj_in.get("email") if is_dict else getattr(obj_in, "email", None)
        if email:
            email = email.lower()

        employee_code = (
            obj_in.get("employee_code")
            if is_dict
            else getattr(obj_in, "employee_code", None)
        )
        role_id = (
            obj_in.get("role_id") if is_dict else getattr(obj_in, "role_id", None)
        )
        department_id = (
            obj_in.get("department_id")
            if is_dict
            else getattr(obj_in, "department_id", None)
        )
        password = (
            obj_in.get("password") if is_dict else getattr(obj_in, "password", None)
        )

        if email:
            existing = await self.repository.get_by_email(email)
            if existing:
                raise ValueError(f"User with email '{email}' already exists.")

        if employee_code:
            existing = await self.repository.get_by_employee_code(employee_code)
            if existing:
                raise ValueError(
                    f"User with employee code '{employee_code}' already exists."
                )

        if role_id:
            role_repo = RoleRepository(self.repository.db)
            role = await role_repo.get(role_id)
            if not role:
                raise ValueError(f"Role with ID '{role_id}' does not exist.")
            if not role.is_active:
                raise ValueError(f"Role '{role.code}' is not active.")
            self._check_role_assignment(current_user, role.code)

        if department_id:
            dept_repo = DepartmentRepository(self.repository.db)
            dept = await dept_repo.get(department_id)
            if not dept:
                raise ValueError(
                    f"Department with ID '{department_id}' does not exist."
                )

        # Hash password and map to password_hash
        data = (
            dict(obj_in)
            if is_dict
            else obj_in.model_dump()
            if hasattr(obj_in, "model_dump")
            else obj_in.__dict__.copy()
        )
        if email:
            data["email"] = email
        password_hash = self._hash_password(password or "defaultpassword")
        data["password_hash"] = password_hash
        if "password" in data:
            del data["password"]
            
        if current_user:
            data["created_by"] = current_user.id

        return await super().create(obj_in=data)

    async def update(
        self, *, id: Any, obj_in: dict[str, Any] | Any, current_user: User | None = None
    ) -> User | None:
        """Update user, verifying email, code, role, and dept."""

        user = await self.repository.get(id)
        if not user:
            return None

        is_dict = isinstance(obj_in, dict)
        email = obj_in.get("email") if is_dict else getattr(obj_in, "email", None)
        if email:
            email = email.lower()

        employee_code = (
            obj_in.get("employee_code")
            if is_dict
            else getattr(obj_in, "employee_code", None)
        )
        role_id = (
            obj_in.get("role_id") if is_dict else getattr(obj_in, "role_id", None)
        )
        department_id = (
            obj_in.get("department_id")
            if is_dict
            else getattr(obj_in, "department_id", None)
        )
        password = (
            obj_in.get("password") if is_dict else getattr(obj_in, "password", None)
        )

        if email:
            existing = await self.repository.get_by_email(email)
            if existing and existing.id != id:
                raise ValueError(f"User with email '{email}' already exists.")

        if employee_code:
            existing = await self.repository.get_by_employee_code(employee_code)
            if existing and existing.id != id:
                raise ValueError(
                    f"User with employee code '{employee_code}' already exists."
                )

        if role_id:
            role_repo = RoleRepository(self.repository.db)
            role = await role_repo.get(role_id)
            if not role:
                raise ValueError(f"Role with ID '{role_id}' does not exist.")
            if not role.is_active:
                raise ValueError(f"Role '{role.code}' is not active.")
            self._check_role_assignment(current_user, role.code)

        if department_id:
            dept_repo = DepartmentRepository(self.repository.db)
            dept = await dept_repo.get(department_id)
            if not dept:
                raise ValueError(
                    f"Department with ID '{department_id}' does not exist."
                )

        data = (
            dict(obj_in)
            if is_dict
            else obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, "model_dump")
            else obj_in.__dict__.copy()
        )
        if email:
            data["email"] = email
        if password:
            data["password_hash"] = self._hash_password(password)
            if "password" in data:
                del data["password"]

        return await super().update(id=id, obj_in=data)

