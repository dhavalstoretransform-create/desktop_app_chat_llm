"""
Authorization and RBAC tests (Phase 4).
"""

from __future__ import annotations

from typing import Any

import pytest
from app.core.database import get_db
from app.main import app
from app.models.department import Department
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.utils.security import create_access_token, hash_password
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def override_db_dependency(memory_db_session: AsyncSession):
    """Override get_db dependency with in-memory SQLite session."""
    async def _get_db_override():
        yield memory_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def setup_rbac_data(memory_db_session: AsyncSession) -> dict[str, Any]:
    """Fixture to create permissions, roles, and users with varying privileges."""
    # 1. Create permissions
    read_role_perm = Permission(
        code="role.read",
        name="Read Roles",
        description="Can list and get roles",
        resource="role",
        action="read",
        is_active=True,
    )
    create_role_perm = Permission(
        code="role.create",
        name="Create Roles",
        description="Can create new roles",
        resource="role",
        action="create",
        is_active=True,
    )
    memory_db_session.add_all([read_role_perm, create_role_perm])
    await memory_db_session.commit()

    # 2. Create departments
    dept = Department(code="ENG", name="Engineering")
    memory_db_session.add(dept)
    await memory_db_session.commit()
    await memory_db_session.refresh(dept)

    # 3. Create admin role and user
    admin_role = Role(code="MANAGER", name="Manager User", is_active=True)
    admin_role.permissions = [read_role_perm, create_role_perm]
    memory_db_session.add(admin_role)
    await memory_db_session.commit()
    await memory_db_session.refresh(admin_role)

    admin_user = User(
        employee_code="EMP_ADMIN",
        full_name="Admin User",
        email="admin@example.com",
        password_hash=hash_password("securepassword"),
        role_id=admin_role.id,
        department_id=dept.id,
    )
    memory_db_session.add(admin_user)

    # 4. Create employee role and user (no permissions)
    employee_role = Role(code="EMPLOYEE", name="Regular Employee")
    memory_db_session.add(employee_role)
    await memory_db_session.commit()
    await memory_db_session.refresh(employee_role)

    employee_user = User(
        employee_code="EMP_EMP",
        full_name="Employee User",
        email="employee@example.com",
        password_hash=hash_password("securepassword"),
        role_id=employee_role.id,
        department_id=dept.id,
    )
    memory_db_session.add(employee_user)

    await memory_db_session.commit()
    await memory_db_session.refresh(admin_user)
    await memory_db_session.refresh(employee_user)

    return {
        "admin_user": admin_user,
        "employee_user": employee_user,
        "read_role_perm": read_role_perm,
        "create_role_perm": create_role_perm,
    }


def test_admin_has_read_permission(client: TestClient, setup_rbac_data: dict[str, Any]):
    """Test that admin with 'read' permission can read roles."""
    admin = setup_rbac_data["admin_user"]
    token = create_access_token(subject=admin.id)

    response = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_employee_lacks_read_permission(
    client: TestClient, setup_rbac_data: dict[str, Any]
):
    """Test that employee without permissions is rejected with 403."""
    employee = setup_rbac_data["employee_user"]
    token = create_access_token(subject=employee.id)

    response = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


@pytest.mark.asyncio
async def test_permission_deactivated(
    client: TestClient, setup_rbac_data: dict[str, Any], memory_db_session: AsyncSession
):
    """Test that if permission is deactivated, user receives 403."""
    admin = setup_rbac_data["admin_user"]
    read_perm = setup_rbac_data["read_role_perm"]

    token = create_access_token(subject=admin.id)

    # Initially allowed
    r1 = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 200

    # Deactivate the permission
    read_perm.is_active = False
    memory_db_session.add(read_perm)
    await memory_db_session.commit()

    # Subsequent access is forbidden
    r2 = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 403


@pytest.mark.asyncio
async def test_role_deactivated(
    client: TestClient, setup_rbac_data: dict[str, Any], memory_db_session: AsyncSession
):
    """Test that if a role is deactivated, it no longer grants permissions."""
    admin = setup_rbac_data["admin_user"]

    token = create_access_token(subject=admin.id)
    r1 = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r1.status_code == 200

    # Retrieve the user's role from the DB and deactivate it
    query = select(Role).where(Role.id == admin.role_id)
    res = await memory_db_session.execute(query)
    role = res.scalar_one()
    role.is_active = False
    memory_db_session.add(role)
    await memory_db_session.commit()

    # Subsequent access should be rejected with 403
    r2 = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 403

