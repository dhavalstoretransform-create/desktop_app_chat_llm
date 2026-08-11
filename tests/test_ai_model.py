"""
Unit tests for the AIModel database model.

Verifies table constraints, attributes, unique name checks, and CRUD transactions.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_model import AIModel


@pytest.mark.asyncio
async def test_create_ai_model_success(memory_db_session: AsyncSession):
    """Test successful model creation with default parameters and constraints."""
    model = AIModel(
        model_name="gpt-4o",
        provider="openai",
        model_version="2024-05-13",
        model_type="chat",
        max_context_tokens=128000,
        input_cost_per_million=Decimal("5.0000"),
        output_cost_per_million=Decimal("15.0000"),
        created_by=uuid.uuid4(),
    )
    memory_db_session.add(model)
    await memory_db_session.commit()
    await memory_db_session.refresh(model)

    assert isinstance(model.id, uuid.UUID)
    assert model.is_active is True
    assert model.model_name == "gpt-4o"
    assert model.input_cost_per_million == Decimal("5.0000")


@pytest.mark.asyncio
async def test_ai_model_name_unique_constraint(memory_db_session: AsyncSession):
    """Test unique constraint on model_name raises IntegrityError."""
    m1 = AIModel(
        model_name="claude-3-5-sonnet",
        provider="anthropic",
        model_type="chat",
        max_context_tokens=200000,
    )
    m2 = AIModel(
        model_name="claude-3-5-sonnet",
        provider="anthropic",
        model_type="chat",
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
    model = AIModel(
        model_name="gemini-1.5-pro",
        provider="google",
        model_type="chat",
        max_context_tokens=2000000,
    )
    memory_db_session.add(model)
    await memory_db_session.commit()

    result = await memory_db_session.execute(
        select(AIModel).where(AIModel.model_name == "gemini-1.5-pro")
    )
    fetched = result.scalar_one()
    assert fetched.provider == "google"
    assert fetched.max_context_tokens == 2000000
