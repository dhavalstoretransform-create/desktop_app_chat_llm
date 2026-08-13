"""
Pytest fixtures — shared across all tests.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from app.core.database import Base
from app.main import app
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    """Synchronous test client — module-scoped for performance."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient]:
    """Async HTTP client for async tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def memory_db_session() -> AsyncGenerator[AsyncSession]:
    """Create in-memory SQLite async session for isolated repository/service testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture(autouse=True)
def auto_mock_authorization(request: pytest.FixtureRequest):
    """Automatically mock authentication and authorization for legacy tests."""
    if (
        "test_auth" in request.node.fspath.strpath
        or "test_rbac" in request.node.fspath.strpath
    ):
        yield
        return

    import uuid
    from unittest.mock import MagicMock

    from app.api.deps import get_current_user
    from app.models.role import Role
    from app.models.user import User

    class AlwaysEqual:
        def __eq__(self, other):
            return True

    mock_permission = MagicMock()
    mock_permission.code = AlwaysEqual()
    mock_permission.is_active = True

    dummy_role = MagicMock(spec=Role)
    dummy_role.code = "ADMIN"
    dummy_role.name = "Admin"
    dummy_role.is_active = True
    dummy_role.permissions = [mock_permission]

    dummy_user = User(
        id=uuid.uuid4(),
        email="test_admin@example.com",
        full_name="Default Admin",
        is_active=True,
        role=dummy_role,
    )

    async def mock_get_current_user():
        return dummy_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield


