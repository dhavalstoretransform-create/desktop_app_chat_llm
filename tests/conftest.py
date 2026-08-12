"""
Pytest fixtures — shared across all tests.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.main import app


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



@pytest.fixture(scope="module")
def client() -> TestClient:
    """Synchronous test client — module-scoped for performance."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Async HTTP client for async tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def memory_db_session() -> AsyncSession:
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

