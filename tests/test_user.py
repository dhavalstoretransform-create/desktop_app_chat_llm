"""
Integration tests for User / Employee API endpoints.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app
from app.models.department import Department
from app.models.role import Role


@pytest.fixture(autouse=True)
def override_db_dependency(memory_db_session: AsyncSession):
    """Override get_db dependency with in-memory SQLite session."""
    async def _get_db_override():
        yield memory_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def prepopulated_relations(
    memory_db_session: AsyncSession,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Helper to create a Role and a Department before creating a User."""
    role = Role(code="STAFF", name="Staff Member")
    dept = Department(code="ENG", name="Engineering")
    memory_db_session.add_all([role, dept])
    await memory_db_session.commit()
    await memory_db_session.refresh(role)
    await memory_db_session.refresh(dept)
    return role.id, dept.id


def test_user_crud_lifecycle(
    client: TestClient, prepopulated_relations: tuple[uuid.UUID, uuid.UUID]
):
    """Test full CRUD operations for users via API."""

    role_id, dept_id = prepopulated_relations

    # 1. Create a User
    create_data = {
        "employee_code": "EMP001",
        "full_name": "Bob Smith",
        "email": "bob@example.com",
        "password": "securepassword123",
        "role_id": str(role_id),
        "department_id": str(dept_id),
        "is_verified": False,
    }
    response = client.post("/api/v1/users/", json=create_data)
    assert response.status_code == 201
    res_data = response.json()
    assert "password_hash" not in res_data
    assert res_data["employee_code"] == "EMP001"
    assert res_data["full_name"] == "Bob Smith"
    assert res_data["email"] == "bob@example.com"
    assert res_data["role_id"] == str(role_id)
    assert res_data["department_id"] == str(dept_id)
    assert "id" in res_data
    assert res_data["is_active"] is True
    user_id = res_data["id"]

    # 2. Prevent duplicate email creation
    dup_email_data = {
        "employee_code": "EMP002",
        "full_name": "Bob Duplicate",
        "email": "bob@example.com",  # Duplicate email
        "password": "securepassword123",
        "role_id": str(role_id),
        "department_id": str(dept_id),
    }
    response_dup = client.post("/api/v1/users/", json=dup_email_data)
    assert response_dup.status_code == 400
    assert "already exists" in response_dup.json()["detail"]

    # 3. Prevent duplicate employee code creation
    dup_code_data = {
        "employee_code": "EMP001",  # Duplicate code
        "full_name": "Bob Duplicate Code",
        "email": "bob2@example.com",
        "password": "securepassword123",
        "role_id": str(role_id),
        "department_id": str(dept_id),
    }
    response_dup_code = client.post("/api/v1/users/", json=dup_code_data)
    assert response_dup_code.status_code == 400
    assert "already exists" in response_dup_code.json()["detail"]

    # 4. Read User by ID
    response_get = client.get(f"/api/v1/users/{user_id}")
    assert response_get.status_code == 200
    res_get_data = response_get.json()
    assert "password_hash" not in res_get_data
    assert res_get_data["employee_code"] == "EMP001"

    # 5. Update User display name
    update_data = {
        "full_name": "Robert Smith",
    }
    response_update = client.patch(f"/api/v1/users/{user_id}", json=update_data)
    assert response_update.status_code == 200
    assert response_update.json()["full_name"] == "Robert Smith"
    assert response_update.json()["employee_code"] == "EMP001"

    # 5b. Test partial update deactivation
    response_deactivate = client.patch(
        f"/api/v1/users/{user_id}", json={"is_active": False}
    )
    assert response_deactivate.status_code == 200
    assert response_deactivate.json()["is_active"] is False
    assert response_deactivate.json()["full_name"] == "Robert Smith"


    # 6. List Users
    response_list = client.get("/api/v1/users/?skip=0&limit=10")
    assert response_list.status_code == 200
    users = response_list.json()
    assert len(users) >= 1
    assert any(u["id"] == user_id for u in users)

    # 7. Soft Delete User
    response_delete = client.delete(f"/api/v1/users/{user_id}")
    assert response_delete.status_code == 200
    assert response_delete.json()["is_active"] is False

    # 8. Non-existent get/update/delete returns 404
    random_id = uuid.uuid4()
    assert client.get(f"/api/v1/users/{random_id}").status_code == 404
    res = client.patch(f"/api/v1/users/{random_id}", json={"full_name": "New"})
    assert res.status_code == 404
    assert client.delete(f"/api/v1/users/{random_id}").status_code == 404

    # 9. Invalid UUID format returns 422
    assert client.get("/api/v1/users/invalid-uuid").status_code == 422
    res_patch = client.patch(
        "/api/v1/users/invalid-uuid", json={"full_name": "New"}
    )
    assert res_patch.status_code == 422
    assert client.delete("/api/v1/users/invalid-uuid").status_code == 422

