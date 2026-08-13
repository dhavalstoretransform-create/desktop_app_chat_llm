"""
Integration tests for Roles and Departments API endpoints.
"""

from __future__ import annotations

import uuid

import pytest
from app.core.database import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def override_db_dependency(memory_db_session: AsyncSession):
    """Override get_db dependency with in-memory SQLite session."""
    async def _get_db_override():
        yield memory_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


def test_role_crud_lifecycle(client: TestClient):
    """Test full CRUD operations for roles via API."""
    # 1. Create a Role
    create_data = {
        "code": "MANAGER",
        "name": "Manager",
        "description": "Department manager role",
    }
    response = client.post("/api/v1/roles/", json=create_data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["code"] == "MANAGER"
    assert res_data["name"] == "Manager"
    assert res_data["description"] == "Department manager role"
    assert "id" in res_data
    assert res_data["is_active"] is True
    role_id = res_data["id"]

    # 2. Prevent duplicate code creation (Business Logic constraint)
    response_dup = client.post(
        "/api/v1/roles/",
        json={
            "code": "MANAGER",
            "name": "Another Manager",
            "description": "Dup code",
        },
    )
    assert response_dup.status_code == 400
    assert "already exists" in response_dup.json()["detail"]

    # 3. Read Role by ID
    response_get = client.get(f"/api/v1/roles/{role_id}")
    assert response_get.status_code == 200
    assert response_get.json()["code"] == "MANAGER"

    # 4. Update Role display name (independent of code)
    update_data = {
        "name": "Senior Manager",
        "description": "Updated manager role description",
    }
    response_update = client.patch(f"/api/v1/roles/{role_id}", json=update_data)
    assert response_update.status_code == 200
    assert response_update.json()["name"] == "Senior Manager"
    assert response_update.json()["code"] == "MANAGER"

    # 5. List Roles (Paginated)
    response_list = client.get("/api/v1/roles/?skip=0&limit=10")
    assert response_list.status_code == 200
    roles = response_list.json()
    assert len(roles) >= 1
    assert any(r["id"] == role_id for r in roles)

    # 6. Soft Delete Role
    response_delete = client.delete(f"/api/v1/roles/{role_id}")
    assert response_delete.status_code == 200
    assert response_delete.json()["is_active"] is False

    # 7. Non-existent get/update/delete returns 404
    random_id = uuid.uuid4()
    assert client.get(f"/api/v1/roles/{random_id}").status_code == 404
    res = client.patch(f"/api/v1/roles/{random_id}", json={"name": "New"})
    assert res.status_code == 404
    assert client.delete(f"/api/v1/roles/{random_id}").status_code == 404

    # 8. Invalid UUID format returns 422
    assert client.get("/api/v1/roles/invalid-uuid").status_code == 422
    assert (
        client.patch("/api/v1/roles/invalid-uuid", json={"name": "New"}).status_code
        == 422
    )
    assert client.delete("/api/v1/roles/invalid-uuid").status_code == 422



def test_department_crud_lifecycle(client: TestClient):
    """Test full CRUD operations for departments via API."""
    # 1. Create a Department
    create_data = {
        "code": "ENG",
        "name": "Engineering",
        "description": "Software engineering department",
    }
    response = client.post("/api/v1/departments/", json=create_data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["code"] == "ENG"
    assert res_data["name"] == "Engineering"
    assert res_data["description"] == "Software engineering department"
    assert "id" in res_data
    assert res_data["is_active"] is True
    dept_id = res_data["id"]

    # 2. Prevent duplicate code creation
    response_dup = client.post(
        "/api/v1/departments/",
        json={
            "code": "ENG",
            "name": "Other Dept",
            "description": "Dup dept code",
        },
    )
    assert response_dup.status_code == 400
    assert "already exists" in response_dup.json()["detail"]

    # 3. Read Department by ID
    response_get = client.get(f"/api/v1/departments/{dept_id}")
    assert response_get.status_code == 200
    assert response_get.json()["code"] == "ENG"

    # 4. Update Department description
    update_data = {"description": "Core R&D department"}
    response_update = client.patch(
        f"/api/v1/departments/{dept_id}", json=update_data
    )
    assert response_update.status_code == 200
    assert response_update.json()["description"] == "Core R&D department"

    # 5. List Departments (Paginated)
    response_list = client.get("/api/v1/departments/?skip=0&limit=10")
    assert response_list.status_code == 200
    depts = response_list.json()
    assert len(depts) >= 1
    assert any(d["id"] == dept_id for d in depts)

    # 6. Soft Delete Department
    response_delete = client.delete(f"/api/v1/departments/{dept_id}")
    assert response_delete.status_code == 200
    assert response_delete.json()["is_active"] is False

    # 7. Non-existent get/update/delete returns 404
    random_id = uuid.uuid4()
    assert client.get(f"/api/v1/departments/{random_id}").status_code == 404
    res = client.patch(f"/api/v1/departments/{random_id}", json={"name": "New"})
    assert res.status_code == 404
    assert client.delete(f"/api/v1/departments/{random_id}").status_code == 404

    # 8. Invalid UUID format returns 422
    assert client.get("/api/v1/departments/invalid-uuid").status_code == 422
    res_patch = client.patch(
        "/api/v1/departments/invalid-uuid", json={"name": "New"}
    )
    assert res_patch.status_code == 422
    assert client.delete("/api/v1/departments/invalid-uuid").status_code == 422

