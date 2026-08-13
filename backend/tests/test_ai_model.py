"""
Unit tests for the AIModel database model.

Verifies table constraints, attributes, unique name checks, and CRUD transactions.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from app.models.ai_model import AIModel
from app.models.ai_provider import AIProvider
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_ai_model_success(memory_db_session: AsyncSession):
    """Test successful model creation with default parameters and constraints."""
    provider = AIProvider(code="openai", name="OpenAI")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    model = AIModel(
        provider_id=provider.id,
        code="gpt-4o",
        name="GPT-4o",
        description="GPT-4o description",
        input_token_price=Decimal("5.0000"),
        output_token_price=Decimal("15.0000"),
        max_context_tokens=128000,
        max_output_tokens=4096,
    )
    memory_db_session.add(model)
    await memory_db_session.commit()
    await memory_db_session.refresh(model)

    assert isinstance(model.id, uuid.UUID)
    assert model.is_active is True
    assert model.code == "gpt-4o"
    assert model.input_token_price == Decimal("5.0000")


@pytest.mark.asyncio
async def test_ai_model_name_unique_constraint(memory_db_session: AsyncSession):
    """Test unique constraint on (provider_id, code) raises IntegrityError."""
    provider = AIProvider(code="anthropic", name="Anthropic")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    m1 = AIModel(
        provider_id=provider.id,
        code="claude-3-5-sonnet",
        name="Claude 3.5 Sonnet",
        max_context_tokens=200000,
    )
    m2 = AIModel(
        provider_id=provider.id,
        code="claude-3-5-sonnet",
        name="Claude 3.5 Sonnet Duplicate",
        max_context_tokens=200000,
    )
    memory_db_session.add(m1)
    await memory_db_session.commit()

    memory_db_session.add(m2)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()

    await memory_db_session.rollback()


@pytest.mark.asyncio
async def test_query_ai_model(memory_db_session: AsyncSession):
    """Test querying AI models."""
    provider = AIProvider(code="google", name="Google")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    model = AIModel(
        provider_id=provider.id,
        code="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        max_context_tokens=2000000,
    )
    memory_db_session.add(model)
    await memory_db_session.commit()

    result = await memory_db_session.execute(
        select(AIModel).where(AIModel.code == "gemini-1.5-pro")
    )
    fetched = result.scalar_one()
    assert fetched.provider_id == provider.id
    assert fetched.max_context_tokens == 2000000
