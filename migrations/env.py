"""
Alembic environment configuration — async SQLAlchemy support.

This file:
  - Reads DATABASE_URL from app.core.config (not from alembic.ini)
  - Uses SQLAlchemy async engine for online migrations
  - Points target_metadata at app.core.database.Base.metadata
    so Alembic can detect model changes automatically

No business models are defined yet (Phase 2+).
The Base.metadata is intentionally empty in Phase 1.
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Make sure backend/ is on sys.path ─────────────────────────────────────────
# This allows `from app.core.config import settings` to work when running
# `alembic` from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
import app.models  # noqa: F401, E402

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Inject DATABASE_URL from application settings (never hardcode in alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from the alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Models metadata for autogenerate support
# Add future model imports here as phases add models.
target_metadata = Base.metadata


# ── Offline migrations (generate SQL without a live DB) ───────────────────────
def run_migrations_offline() -> None:
    """Run migrations in offline mode (generates SQL scripts)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations (run against a live DB) ─────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode (against a live database)."""
    # psycopg3 async requires SelectorEventLoop on Windows (not ProactorEventLoop)
    import sys
    if sys.platform == "win32":
        import selectors
        asyncio.set_event_loop_policy(
            asyncio.DefaultEventLoopPolicy()
        )
        loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_async_migrations())
        finally:
            loop.close()
    else:
        asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
