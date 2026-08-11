"""
Tests for the health check endpoint and root level redirections.

Phase 1 deliverable: GET /health → {"status": "ok"}
"""

from __future__ import annotations

import pytest


class TestRootHealth:
    """GET /health — root level, unauthenticated."""

    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_status_ok(self, client):
        data = client.get("/health").json()
        assert data == {"status": "ok"}

    def test_content_type_is_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]


class TestV1Health:
    """GET /api/v1/health — versioned endpoint."""

    def test_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_returns_status_ok(self, client):
        data = client.get("/api/v1/health").json()
        assert data == {"status": "ok"}


class TestRootRoutes:
    """Root welcome and documentation redirect tests."""

    def test_root_welcome_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ChatLLM"
        assert data["status"] == "ok"

    def test_docs_redirect(self, client):
        # We disable redirect following to check the redirect header status
        response = client.get("/docs", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/api/v1/docs"


class TestAsyncHealth:
    """Async client smoke tests."""

    @pytest.mark.asyncio
    async def test_root_health_async(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
