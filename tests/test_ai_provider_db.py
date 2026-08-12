"""
Comprehensive database-level unit tests for AI Provider and AI Model models.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_model import AIModel
from app.models.ai_provider import AIProvider
from app.repositories.ai_model import AIModelRepository
from app.repositories.ai_provider import AIProviderRepository


@pytest.mark.asyncio
async def test_ai_provider_comprehensive_db_ops(memory_db_session: AsyncSession):
    """Test AIProvider constraints, fields, repository methods, and active status."""
    repo = AIProviderRepository(memory_db_session)

    # 1. Create provider & 3. Required fields (code, name)
    provider = AIProvider(
        code="openai",
        name="OpenAI",
        description="OpenAI LLM provider",
    )
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id
    assert provider_id is not None
    assert provider.code == "openai"
    assert provider.name == "OpenAI"
    # 4. Active status default is True
    assert provider.is_active is True

    # 2. Provider code uniqueness
    dup_provider = AIProvider(
        code="openai",
        name="Duplicate OpenAI",
    )
    memory_db_session.add(dup_provider)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 5. Get provider by code
    fetched = await repo.get_by_code("openai")
    assert fetched is not None
    assert fetched.id == provider_id

    # 6. Update provider
    fetched.name = "OpenAI Inc"
    await memory_db_session.commit()
    await memory_db_session.refresh(fetched)
    assert fetched.name == "OpenAI Inc"

    # 7. Deactivate provider
    fetched.is_active = False
    await memory_db_session.commit()
    await memory_db_session.refresh(fetched)
    assert fetched.is_active is False


@pytest.mark.asyncio
async def test_ai_model_creation_and_uniqueness(memory_db_session: AsyncSession):
    """Test AIModel creation, provider association, and uniqueness within provider."""
    provider = AIProvider(code="openai", name="OpenAI")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id

    # 8. Create model & 9. Model belongs to provider
    model = AIModel(
        provider_id=provider_id,
        code="gpt-4",
        name="GPT-4",
        description="GPT-4 model description",
        input_token_price=Decimal("30.0000"),
        output_token_price=Decimal("60.0000"),
        max_context_tokens=8192,
        max_output_tokens=4096,
    )
    memory_db_session.add(model)
    await memory_db_session.commit()
    await memory_db_session.refresh(model)

    assert model.id is not None
    assert model.provider_id == provider_id
    assert model.is_active is True
    assert model.input_token_price == Decimal("30.0000")

    # 10. Model code uniqueness within provider
    dup_model = AIModel(
        provider_id=provider_id,
        code="gpt-4",
        name="Duplicate GPT-4",
    )
    memory_db_session.add(dup_model)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 11. Same model code under different providers is allowed
    provider2 = AIProvider(code="google", name="Google")
    memory_db_session.add(provider2)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider2)

    model2 = AIModel(
        provider_id=provider2.id,
        code="gpt-4",  # Same code
        name="Google GPT-4",
    )
    memory_db_session.add(model2)
    await memory_db_session.commit()
    assert model2.id is not None


@pytest.mark.asyncio
async def test_ai_model_invalid_pricing(memory_db_session: AsyncSession):
    """Test 15. Negative pricing rejected constraint."""
    provider = AIProvider(code="openai", name="OpenAI")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id

    invalid_price_model = AIModel(
        provider_id=provider_id,
        code="gpt-neg",
        name="Negative Price model",
        input_token_price=Decimal("-1.0000"),
    )
    memory_db_session.add(invalid_price_model)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()


@pytest.mark.asyncio
async def test_ai_model_invalid_limits(memory_db_session: AsyncSession):
    """Test 16. Context limit and 17. Output limit positive constraints."""
    provider = AIProvider(code="openai", name="OpenAI")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id

    # Context limit positive constraint check
    invalid_ctx_model = AIModel(
        provider_id=provider_id,
        code="gpt-ctx",
        name="Invalid Ctx model",
        max_context_tokens=0,
    )
    memory_db_session.add(invalid_ctx_model)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # Output limit positive constraint check
    invalid_out_model = AIModel(
        provider_id=provider_id,
        code="gpt-out",
        name="Invalid Out model",
        max_output_tokens=-10,
    )
    memory_db_session.add(invalid_out_model)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()


@pytest.mark.asyncio
async def test_ai_model_queries_and_deactivation(memory_db_session: AsyncSession):
    """Test repository query methods, updates, and deactivation."""
    model_repo = AIModelRepository(memory_db_session)

    provider = AIProvider(code="openai", name="OpenAI")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id

    model = AIModel(
        provider_id=provider_id,
        code="gpt-4",
        name="GPT-4",
    )
    memory_db_session.add(model)
    await memory_db_session.commit()
    await memory_db_session.refresh(model)

    # 18. Get model by provider/code
    fetched_model = await model_repo.get_by_code_and_provider(
        code="gpt-4", provider_id=provider_id
    )
    assert fetched_model is not None
    assert fetched_model.id == model.id

    # 19. List models by provider
    models_list = await model_repo.get_multi_by_provider(provider_id=provider_id)
    assert len(models_list) == 1
    assert models_list[0].id == model.id

    # 20. Update model
    model.name = "GPT-4 Improved"
    await memory_db_session.commit()
    await memory_db_session.refresh(model)
    assert model.name == "GPT-4 Improved"

    # 21. Deactivate model
    model.is_active = False
    await memory_db_session.commit()
    await memory_db_session.refresh(model)
    assert model.is_active is False


@pytest.mark.asyncio
async def test_ai_provider_relationships_and_safety(memory_db_session: AsyncSession):
    """Test relationships, deletion protection, invalid foreign keys, and rollbacks."""
    provider = AIProvider(code="anthropic", name="Anthropic")
    memory_db_session.add(provider)
    await memory_db_session.commit()
    await memory_db_session.refresh(provider)

    provider_id = provider.id

    model1 = AIModel(
        provider_id=provider_id,
        code="claude-3",
        name="Claude 3",
    )
    model2 = AIModel(
        provider_id=provider_id,
        code="claude-3.5",
        name="Claude 3.5",
    )
    memory_db_session.add_all([model1, model2])
    await memory_db_session.commit()

    # 22. Provider -> models relationship (eager load using selectinload)
    query = (
        select(AIProvider)
        .where(AIProvider.id == provider_id)
        .options(selectinload(AIProvider.models))
    )
    res = await memory_db_session.execute(query)
    provider_loaded = res.scalar_one()
    assert len(provider_loaded.models) == 2
    assert any(m.code == "claude-3" for m in provider_loaded.models)

    # 23. Model -> provider relationship (eager load using selectinload)
    query2 = (
        select(AIModel)
        .where(AIModel.id == model1.id)
        .options(selectinload(AIModel.provider))
    )
    res2 = await memory_db_session.execute(query2)
    model_loaded = res2.scalar_one()
    assert model_loaded.provider is not None
    assert model_loaded.provider.code == "anthropic"

    # 24. Provider deletion protection (RESTRICT)
    await memory_db_session.delete(provider_loaded)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    # 26. Transaction rollback works
    await memory_db_session.rollback()

    # Verify provider still exists after rollback
    query_check = select(AIProvider).where(AIProvider.id == provider_id)
    res_check = await memory_db_session.execute(query_check)
    assert res_check.scalar_one_or_none() is not None

    # 25. Invalid provider rejected
    bad_model = AIModel(
        provider_id=uuid.uuid4(),  # Non-existent ID
        code="bad-model",
        name="Bad Model",
    )
    memory_db_session.add(bad_model)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()
