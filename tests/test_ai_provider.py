"""
Integration and security tests for AI Provider and AI Model API endpoints.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app


@pytest.fixture(autouse=True)
def override_db_dependency(memory_db_session: AsyncSession):
    """Override get_db dependency with in-memory SQLite session."""
    async def _get_db_override():
        yield memory_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


def test_ai_provider_api_crud_and_conflicts(client: TestClient):
    """Test AI Provider CRUD, duplicate codes, validation, and credentials exposure."""
    # 27. Create Provider
    create_res = client.post(
        "/api/v1/ai-providers/",
        json={"code": "openai", "name": "OpenAI", "description": "AI Provider"},
    )
    assert create_res.status_code == 201
    provider = create_res.json()
    assert provider["code"] == "openai"
    provider_id = provider["id"]

    # 34. Credentials are never exposed
    # 35. No API key, 36. No provider secret, 37. No credentials endpoint
    # Verify no credential/secret keys exist in response fields
    for key in ["api_key", "secret", "password", "credential", "token"]:
        assert key not in provider

    # 30. Duplicate provider code returns conflict (400)
    dup_res = client.post(
        "/api/v1/ai-providers/",
        json={"code": "openai", "name": "Duplicate OpenAI"},
    )
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # Update Provider
    patch_res = client.patch(
        f"/api/v1/ai-providers/{provider_id}",
        json={"name": "OpenAI Corp"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "OpenAI Corp"

    # Read Provider
    get_res = client.get(f"/api/v1/ai-providers/{provider_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "OpenAI Corp"

    # Soft Delete / Deactivate Provider
    del_res = client.delete(f"/api/v1/ai-providers/{provider_id}")
    assert del_res.status_code == 200
    assert del_res.json()["is_active"] is False


def test_ai_model_api_crud_and_filtering(client: TestClient):
    """Test AI Model CRUD, duplicate conflicts, filtering, and invalid pricing."""
    # Create Provider first
    provider_res = client.post(
        "/api/v1/ai-providers/",
        json={"code": "anthropic", "name": "Anthropic"},
    )
    assert provider_res.status_code == 201
    provider_id = provider_res.json()["id"]

    # 28. Create Model
    create_res = client.post(
        "/api/v1/ai-models/",
        json={
            "provider_id": provider_id,
            "code": "claude-3",
            "name": "Claude 3",
            "input_token_price": 3.00,
            "output_token_price": 15.00,
        },
    )
    assert create_res.status_code == 201
    model = create_res.json()
    assert model["code"] == "claude-3"
    model_id = model["id"]

    # 31. Duplicate model code for same provider returns conflict (400)
    dup_res = client.post(
        "/api/v1/ai-models/",
        json={
            "provider_id": provider_id,
            "code": "claude-3",
            "name": "Claude 3 duplicate",
        },
    )
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # 32. Invalid provider returns appropriate error (404)
    bad_provider_res = client.post(
        "/api/v1/ai-models/",
        json={
            "provider_id": str(uuid.uuid4()),
            "code": "gpt-bad",
            "name": "Bad model",
        },
    )
    assert bad_provider_res.status_code == 404

    # 33. Invalid pricing returns validation error (422)
    invalid_price_res = client.post(
        "/api/v1/ai-models/",
        json={
            "provider_id": provider_id,
            "code": "gpt-invalid-price",
            "name": "Invalid Price",
            "input_token_price": -2.50,
        },
    )
    assert invalid_price_res.status_code == 422

    # Update Model
    patch_res = client.patch(
        f"/api/v1/ai-models/{model_id}",
        json={"name": "Claude 3.1"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Claude 3.1"

    # Read Model
    get_res = client.get(f"/api/v1/ai-models/{model_id}")
    assert get_res.status_code == 200

    # 29. Model filtering by provider
    filter_res = client.get(f"/api/v1/ai-models/?provider_id={provider_id}")
    assert filter_res.status_code == 200
    assert len(filter_res.json()) == 1
    assert filter_res.json()[0]["id"] == model_id

    # Filter with non-existent provider returns empty list
    empty_filter_res = client.get(f"/api/v1/ai-models/?provider_id={uuid.uuid4()}")
    assert empty_filter_res.status_code == 200
    assert len(empty_filter_res.json()) == 0

    # Soft Delete / Deactivate Model
    del_res = client.delete(f"/api/v1/ai-models/{model_id}")
    assert del_res.status_code == 200
    assert del_res.json()["is_active"] is False
