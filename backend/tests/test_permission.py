"""
Integration tests for Permission API endpoints.
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


def test_permission_crud_lifecycle(client: TestClient):
    """Test full CRUD operations for permissions via API."""
    # 1. Create a Permission
    create_data = {
        "code": "user.create",
        "name": "Create Users",
        "description": "Allows creating new users",
        "resource": "user",
        "action": "create",
    }
    response = client.post("/api/v1/permissions/", json=create_data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["code"] == "user.create"
    assert res_data["name"] == "Create Users"
    assert res_data["resource"] == "user"
    assert res_data["action"] == "create"
    assert res_data["is_active"] is True
    assert "id" in res_data
    perm_id = res_data["id"]

    # 2. Prevent duplicate code creation
    response_dup = client.post(
        "/api/v1/permissions/",
        json={
            "code": "user.create",
            "name": "Dup Create",
            "resource": "user",
            "action": "create",
        },
    )
    assert response_dup.status_code == 400
    assert "already exists" in response_dup.json()["detail"]

    # 3. Read Permission by ID
    response_get = client.get(f"/api/v1/permissions/{perm_id}")
    assert response_get.status_code == 200
    assert response_get.json()["code"] == "user.create"

    # 4. Update Permission display name
    update_data = {
        "name": "Super Create Users",
    }
    response_update = client.patch(
        f"/api/v1/permissions/{perm_id}", json=update_data
    )
    assert response_update.status_code == 200
    assert response_update.json()["name"] == "Super Create Users"

    # 5. List Permissions
    response_list = client.get("/api/v1/permissions/?skip=0&limit=10")
    assert response_list.status_code == 200
    perms = response_list.json()
    assert len(perms) >= 1
    assert any(p["id"] == perm_id for p in perms)

    # 6. Soft Delete Permission
    response_delete = client.delete(f"/api/v1/permissions/{perm_id}")
    assert response_delete.status_code == 200
    assert response_delete.json()["is_active"] is False

    # 7. Non-existent get/update/delete returns 404
    random_id = uuid.uuid4()
    assert client.get(f"/api/v1/permissions/{random_id}").status_code == 404
    res = client.patch(f"/api/v1/permissions/{random_id}", json={"name": "New"})
    assert res.status_code == 404
    assert client.delete(f"/api/v1/permissions/{random_id}").status_code == 404


def test_role_permission_assignment_api(client: TestClient):
    """Test assigning and listing permissions for a role via API."""
    # 1. Create a Role
    role_res = client.post(
        "/api/v1/roles/",
        json={"code": "MANAGER", "name": "Manager Role"},
    )
    assert role_res.status_code == 201
    role_id = role_res.json()["id"]

    # 2. Create Permissions
    perm1_res = client.post(
        "/api/v1/permissions/",
        json={
            "code": "chat.create",
            "name": "Create Chat",
            "resource": "chat",
            "action": "create",
        },
    )
    assert perm1_res.status_code == 201
    perm1_id = perm1_res.json()["id"]

    perm2_res = client.post(
        "/api/v1/permissions/",
        json={
            "code": "chat.read",
            "name": "Read Chat",
            "resource": "chat",
            "action": "read",
        },
    )
    assert perm2_res.status_code == 201
    perm2_id = perm2_res.json()["id"]

    # 3. Assign Permissions to Role (Success Case)
    assign_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=[perm1_id, perm2_id],
    )
    assert assign_res.status_code == 200
    assigned = assign_res.json()
    assert len(assigned) == 2
    assert any(p["id"] == perm1_id for p in assigned)
    assert any(p["id"] == perm2_id for p in assigned)

    # 4. List Permissions assigned to Role
    list_res = client.get(f"/api/v1/roles/{role_id}/permissions")
    assert list_res.status_code == 200
    list_assigned_res = list_res.json()
    assert list_assigned_res["message"] == "Role permissions retrieved successfully."
    list_assigned = list_assigned_res["data"]
    assert len(list_assigned) == 2

    # 5. Nonexistent role + valid permission -> 404
    bad_role_id = uuid.uuid4()
    bad_role_res = client.post(
        f"/api/v1/roles/{bad_role_id}/permissions",
        json=[perm1_id],
    )
    assert bad_role_res.status_code == 404

    # 6. Valid role + nonexistent permission -> 404
    bad_perm_id = uuid.uuid4()
    bad_perm_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=[str(bad_perm_id)],
    )
    assert bad_perm_res.status_code == 404
    assert f"Permission not found: {bad_perm_id}" in bad_perm_res.json()["detail"]

    # 7. Valid role + one valid + one nonexistent permission -> 404
    # Ensure role permissions did not change (atomic check)
    mixed_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=[perm1_id, str(bad_perm_id)],
    )
    assert mixed_res.status_code == 404

    # Re-verify permissions are still the original 2 (no partial modifications)
    list_res2 = client.get(f"/api/v1/roles/{role_id}/permissions")
    assert len(list_res2.json()["data"]) == 2

    # 8. Duplicate permission assignment -> Success, no duplicates
    dup_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=[perm1_id, perm1_id],
    )
    assert dup_res.status_code == 200
    assert len(dup_res.json()) == 1

    # 9. Empty permission array -> 400 Bad Request
    empty_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=[],
    )
    assert empty_res.status_code == 400

    # 10. Invalid permission UUID format -> 422
    invalid_format_res = client.post(
        f"/api/v1/roles/{role_id}/permissions",
        json=["invalid-permission-uuid"],
    )
    assert invalid_format_res.status_code == 422

    # 11. GET Role permissions: nonexistent role -> 404
    assert client.get(f"/api/v1/roles/{uuid.uuid4()}/permissions").status_code == 404

    # 12. GET Role permissions: invalid UUID format -> 422
    assert client.get("/api/v1/roles/invalid-uuid/permissions").status_code == 422

    # 13. GET Role permissions: existing role with no permissions -> 200 []
    empty_role_res = client.post(
        "/api/v1/roles/",
        json={"code": "EMPTY_ROLE", "name": "Empty Role"},
    )
    empty_role_id = empty_role_res.json()["id"]
    empty_get_res = client.get(f"/api/v1/roles/{empty_role_id}/permissions")
    assert empty_get_res.status_code == 200
    assert (
        empty_get_res.json()["message"]
        == "No permissions are assigned to this role."
    )
    assert empty_get_res.json()["data"] == []

    # 14. Invalid UUID format on Permission CRUD routes -> 422
    assert client.get("/api/v1/permissions/invalid-uuid").status_code == 422
    res_patch = client.patch(
        "/api/v1/permissions/invalid-uuid", json={"name": "New"}
    )
    assert res_patch.status_code == 422
    assert client.delete("/api/v1/permissions/invalid-uuid").status_code == 422


