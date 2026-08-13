"""
Comprehensive Authorization and RBAC tests (Phase 4).
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from app.core.database import get_db
from app.main import app
from app.models.audit import AuditLog
from app.models.department import Department
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.utils.security import create_access_token, hash_password
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
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
async def setup_comprehensive_data(memory_db_session: AsyncSession) -> dict[str, Any]:
    """Seed base roles, permissions, department, and users for comprehensive testing."""
    # Seed Permissions
    permissions_to_add = [
        Permission(
            code="role.create",
            name="Create Role",
            resource="role",
            action="create",
            is_active=True,
        ),
        Permission(
            code="role.read",
            name="Read Role",
            resource="role",
            action="read",
            is_active=True,
        ),
        Permission(
            code="role.update",
            name="Update Role",
            resource="role",
            action="update",
            is_active=True,
        ),
        Permission(
            code="role.deactivate",
            name="Deactivate Role",
            resource="role",
            action="deactivate",
            is_active=True,
        ),
        Permission(
            code="department.create",
            name="Create Dept",
            resource="department",
            action="create",
            is_active=True,
        ),
        Permission(
            code="department.read",
            name="Read Dept",
            resource="department",
            action="read",
            is_active=True,
        ),
        Permission(
            code="department.update",
            name="Update Dept",
            resource="department",
            action="update",
            is_active=True,
        ),
        Permission(
            code="department.deactivate",
            name="Deactivate Dept",
            resource="department",
            action="deactivate",
            is_active=True,
        ),
        Permission(
            code="user.create",
            name="Create User",
            resource="user",
            action="create",
            is_active=True,
        ),
        Permission(
            code="user.read",
            name="Read User",
            resource="user",
            action="read",
            is_active=True,
        ),
        Permission(
            code="user.update",
            name="Update User",
            resource="user",
            action="update",
            is_active=True,
        ),
        Permission(
            code="user.deactivate",
            name="Deactivate User",
            resource="user",
            action="deactivate",
            is_active=True,
        ),
        Permission(
            code="permission.create",
            name="Create Perm",
            resource="permission",
            action="create",
            is_active=True,
        ),
        Permission(
            code="permission.read",
            name="Read Perm",
            resource="permission",
            action="read",
            is_active=True,
        ),
        Permission(
            code="permission.update",
            name="Update Perm",
            resource="permission",
            action="update",
            is_active=True,
        ),
        Permission(
            code="permission.deactivate",
            name="Deactivate Perm",
            resource="permission",
            action="deactivate",
            is_active=True,
        ),
        Permission(
            code="permission.assign",
            name="Assign Perm",
            resource="permission",
            action="assign",
            is_active=True,
        ),
    ]
    memory_db_session.add_all(permissions_to_add)
    await memory_db_session.commit()

    # Seed Department
    dept = Department(code="HR", name="Human Resources")
    memory_db_session.add(dept)
    await memory_db_session.commit()
    await memory_db_session.refresh(dept)

    # Seed Admin Role (active, owns all permissions)
    admin_role = Role(code="COMP_ADMIN", name="Comp Admin", is_active=True)
    admin_role.permissions = permissions_to_add
    memory_db_session.add(admin_role)
    await memory_db_session.commit()
    await memory_db_session.refresh(admin_role)

    # Seed Employee Role (active, owns only user.read)
    user_read_perm = next(p for p in permissions_to_add if p.code == "user.read")
    employee_role = Role(code="COMP_EMPLOYEE", name="Comp Employee", is_active=True)
    employee_role.permissions = [user_read_perm]
    memory_db_session.add(employee_role)
    await memory_db_session.commit()
    await memory_db_session.refresh(employee_role)

    # Seed Users
    admin_user = User(
        employee_code="HR_ADMIN",
        full_name="HR Administrator",
        email="hr_admin@example.com",
        password_hash=hash_password("password123"),
        role_id=admin_role.id,
        department_id=dept.id,
        is_active=True,
    )
    employee_user = User(
        employee_code="HR_STAFF",
        full_name="HR Staff Member",
        email="hr_staff@example.com",
        password_hash=hash_password("password123"),
        role_id=employee_role.id,
        department_id=dept.id,
        is_active=True,
    )
    memory_db_session.add_all([admin_user, employee_user])
    await memory_db_session.commit()
    await memory_db_session.refresh(admin_user)
    await memory_db_session.refresh(employee_user)

    # Map details for tests
    mapped_perms = {p.code: p for p in permissions_to_add}

    return {
        "admin_user": admin_user,
        "employee_user": employee_user,
        "admin_role": admin_role,
        "employee_role": employee_role,
        "permissions": mapped_perms,
        "department": dept,
    }


# ── SECTION 1: Core Authentication & Authorization Requirements ─────────────────


@pytest.mark.asyncio
async def test_auth_and_rbac_core_scenarios(
    client: TestClient,
    setup_comprehensive_data: dict[str, Any],
    memory_db_session: AsyncSession,
):
    data = setup_comprehensive_data
    admin = data["admin_user"]
    employee = data["employee_user"]

    # 1. Valid authenticated user
    token = create_access_token(subject=admin.id)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200

    # 2. Unauthenticated request
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

    # 3. Invalid JWT
    res = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert res.status_code == 401

    from datetime import timedelta

    expired_token = create_access_token(
        subject=admin.id, expires_delta=timedelta(seconds=-3600)
    )
    res = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res.status_code == 401

    # 5. Active user with required permission (admin accesses role list)
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 200

    # 6. Active user without required permission (employee accesses role list)
    emp_token = create_access_token(subject=employee.id)
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    res = client.get("/api/v1/roles/", headers=emp_headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "Insufficient permissions"

    # 7. Inactive user (deactivate admin user)
    admin.is_active = False
    memory_db_session.add(admin)
    await memory_db_session.commit()
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 400  # get_current_user returns 400 for inactive user
    admin.is_active = True
    memory_db_session.add(admin)
    await memory_db_session.commit()

    # 8. Inactive role
    role = data["admin_role"]
    role.is_active = False
    memory_db_session.add(role)
    await memory_db_session.commit()
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 403
    role.is_active = True
    memory_db_session.add(role)
    await memory_db_session.commit()

    # 9. Inactive permission
    perm = data["permissions"]["role.read"]
    perm.is_active = False
    memory_db_session.add(perm)
    await memory_db_session.commit()
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 403
    perm.is_active = True
    memory_db_session.add(perm)
    await memory_db_session.commit()

    # 10. Multiple permissions assigned to role
    # admin_role has 17 permissions seeded, let's verify both
    # role.read and user.read work
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 200
    res = client.get("/api/v1/users/", headers=headers)
    assert res.status_code == 200

    # 11. Permission assignment removed
    # Remove user.read from admin_role permissions list
    role = data["admin_role"]
    role.permissions = [p for p in role.permissions if p.code != "user.read"]
    memory_db_session.add(role)
    await memory_db_session.commit()
    res = client.get("/api/v1/users/", headers=headers)
    assert res.status_code == 403

    # 12. Permission assignment restored
    user_read_perm = data["permissions"]["user.read"]
    role.permissions.append(user_read_perm)
    memory_db_session.add(role)
    await memory_db_session.commit()
    res = client.get("/api/v1/users/", headers=headers)
    assert res.status_code == 200

    # 13. Role changed for user
    # Change admin's role to employee_role (which doesn't have role.read)
    admin.role = data["employee_role"]
    memory_db_session.add(admin)
    await memory_db_session.commit()
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 403

    # 14. User receives new role permissions dynamically
    # Assign role.read to employee_role
    data["employee_role"].permissions.append(data["permissions"]["role.read"])
    memory_db_session.add(data["employee_role"])
    await memory_db_session.commit()
    res = client.get("/api/v1/roles/", headers=headers)
    assert res.status_code == 200

    # Restore admin role
    admin.role = data["admin_role"]
    memory_db_session.add(admin)
    await memory_db_session.commit()

    # Restore employee role permissions (remove role.read)
    data["employee_role"].permissions = [
        p for p in data["employee_role"].permissions if p.code != "role.read"
    ]
    memory_db_session.add(data["employee_role"])
    await memory_db_session.commit()

    # 15. No permission hardcoded into JWT
    import jwt

    unverified = jwt.decode(token, options={"verify_signature": False})
    assert "permissions" not in unverified
    assert "permission" not in unverified

    # 16. Authorization failure returns 403
    # Already demonstrated by status check and assert res.status_code == 403

    # 17. Authentication failure returns 401
    # Already demonstrated by unauthenticated and expired token checks

    # 18. Authorization failure audit is recorded
    # Call user endpoint with regular employee token lacking role.read
    # (which triggers failure audit log)
    # Clear audit logs first to verify
    await memory_db_session.execute(delete(AuditLog))
    await memory_db_session.commit()

    res = client.get("/api/v1/roles/", headers=emp_headers)
    assert res.status_code == 403

    audit_query = select(AuditLog).where(AuditLog.action == "AUTHORIZATION_FAILED")
    audit_res = await memory_db_session.execute(audit_query)
    log = audit_res.scalars().first()
    assert log is not None
    assert log.user_id == employee.id
    assert log.description is not None
    assert "role.read" in log.description


# ── SECTION 2: CRUD Authorization Tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_crud_endpoints_authorization(
    client: TestClient,
    setup_comprehensive_data: dict[str, Any],
):
    data = setup_comprehensive_data
    admin_token = create_access_token(subject=data["admin_user"].id)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    emp_token = create_access_token(subject=data["employee_user"].id)
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # ── Roles ──
    # authorized create
    res = client.post(
        "/api/v1/roles/",
        json={"code": "TEST_R", "name": "Test Role"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    role_uuid = uuid.UUID(res.json()["id"])
    # unauthorized create
    res = client.post(
        "/api/v1/roles/",
        json={"code": "TEST_U", "name": "Test Role"},
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized update
    res = client.patch(
        f"/api/v1/roles/{role_uuid}", json={"name": "New Name"}, headers=admin_headers
    )
    assert res.status_code == 200
    # unauthorized update
    res = client.patch(
        f"/api/v1/roles/{role_uuid}", json={"name": "Bad Name"}, headers=emp_headers
    )
    assert res.status_code == 403
    # authorized deactivate
    res = client.delete(f"/api/v1/roles/{role_uuid}", headers=admin_headers)
    assert res.status_code == 200
    # unauthorized deactivate (we make a dummy role to test unauthorized delete)
    dummy_r = client.post(
        "/api/v1/roles/", json={"code": "DUM_R", "name": "Dum"}, headers=admin_headers
    )
    assert dummy_r.status_code == 201
    dum_uuid = dummy_r.json()["id"]
    res = client.delete(f"/api/v1/roles/{dum_uuid}", headers=emp_headers)
    assert res.status_code == 403

    # ── Departments ──
    # authorized create
    res = client.post(
        "/api/v1/departments/",
        json={"code": "T_D", "name": "Test Dept"},
        headers=admin_headers,
    )
    assert res.status_code == 201
    dept_uuid = uuid.UUID(res.json()["id"])
    # unauthorized create
    res = client.post(
        "/api/v1/departments/",
        json={"code": "U_D", "name": "Bad Dept"},
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized update
    res = client.patch(
        f"/api/v1/departments/{dept_uuid}",
        json={"name": "New Dept Name"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    # unauthorized update
    res = client.patch(
        f"/api/v1/departments/{dept_uuid}",
        json={"name": "Bad Dept Name"},
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized deactivate
    res = client.delete(f"/api/v1/departments/{dept_uuid}", headers=admin_headers)
    assert res.status_code == 200
    # unauthorized deactivate
    res = client.delete(
        f"/api/v1/departments/{data['department'].id}", headers=emp_headers
    )
    assert res.status_code == 403

    # ── Users ──
    # authorized create
    res = client.post(
        "/api/v1/users/",
        json={
            "employee_code": "E_CR",
            "full_name": "Create User",
            "email": "cr@example.com",
            "password": "password",
            "role_id": str(data["employee_role"].id),
            "department_id": str(data["department"].id),
        },
        headers=admin_headers,
    )
    assert res.status_code == 201
    user_uuid = uuid.UUID(res.json()["id"])
    # unauthorized create
    res = client.post(
        "/api/v1/users/",
        json={
            "employee_code": "E_UNCR",
            "full_name": "Create User",
            "email": "uncr@example.com",
            "password": "password",
            "role_id": str(data["employee_role"].id),
            "department_id": str(data["department"].id),
        },
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized update
    res = client.patch(
        f"/api/v1/users/{user_uuid}",
        json={"full_name": "New User Name"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    # unauthorized update
    res = client.patch(
        f"/api/v1/users/{user_uuid}",
        json={"full_name": "Bad User Name"},
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized deactivate
    res = client.delete(f"/api/v1/users/{user_uuid}", headers=admin_headers)
    assert res.status_code == 200
    # unauthorized deactivate
    res = client.delete(
        f"/api/v1/users/{data['employee_user'].id}", headers=emp_headers
    )
    assert res.status_code == 403

    # ── Permissions ──
    # authorized create (authorized management)
    res = client.post(
        "/api/v1/permissions/",
        json={
            "code": "test.action",
            "name": "Test Perm",
            "description": "Allows testing",
            "resource": "test",
            "action": "action",
        },
        headers=admin_headers,
    )
    assert res.status_code == 201
    perm_uuid = uuid.UUID(res.json()["id"])
    # unauthorized create (unauthorized management)
    res = client.post(
        "/api/v1/permissions/",
        json={
            "code": "bad.action",
            "name": "Bad Perm",
            "description": "Allows testing",
            "resource": "test",
            "action": "action",
        },
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized update
    res = client.patch(
        f"/api/v1/permissions/{perm_uuid}",
        json={"name": "New Name"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    # unauthorized update
    res = client.patch(
        f"/api/v1/permissions/{perm_uuid}",
        json={"name": "Bad Name"},
        headers=emp_headers,
    )
    assert res.status_code == 403
    # authorized deactivate
    res = client.delete(f"/api/v1/permissions/{perm_uuid}", headers=admin_headers)
    assert res.status_code == 200
    # unauthorized deactivate
    dummy_p = client.post(
        "/api/v1/permissions/",
        json={
            "code": "dum.action",
            "name": "Dum Perm",
            "description": "Allows testing",
            "resource": "test",
            "action": "action",
        },
        headers=admin_headers,
    )
    assert dummy_p.status_code == 201
    dum_perm_uuid = dummy_p.json()["id"]
    res = client.delete(f"/api/v1/permissions/{dum_perm_uuid}", headers=emp_headers)
    assert res.status_code == 403

    # ── Role Permissions Assignment ──
    # authorized assignment
    res = client.post(
        f"/api/v1/roles/{role_uuid}/permissions",
        json=[str(dum_perm_uuid)],
        headers=admin_headers,
    )
    assert res.status_code == 200
    # unauthorized assignment
    res = client.post(
        f"/api/v1/roles/{role_uuid}/permissions",
        json=[str(dum_perm_uuid)],
        headers=emp_headers,
    )
    assert res.status_code == 403
