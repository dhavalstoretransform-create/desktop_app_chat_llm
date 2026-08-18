import uuid
from decimal import Decimal
from datetime import datetime, timezone
import pytest
from unittest.mock import patch, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.models.ai_model import AIModel
from app.models.ai_provider import AIProvider
from app.models.user import User
from app.models.wallet import EmployeeTokenWallet
from app.models.token_transaction import TokenTransaction
from app.models.prompt_log import PromptLog
from app.models.usage import TokenUsage
from app.models.audit import AuditLog
from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.models.setting import SystemSetting

# Mock gateway result for tests
SUCCESS_GATEWAY_RESULT = {
    "content": "This is a real AI response.",
    "input_tokens": 10,
    "output_tokens": 20,
    "total_tokens": 30,
    "response_time_ms": 1500
}

@pytest.fixture
async def setup_chat_test_data(memory_db_session: AsyncSession):
    # Create test user
    user = User(
        id=uuid.uuid4(),
        employee_code="TEST-CHAT-01",
        full_name="Chat User",
        email="chatuser@example.com",
        password_hash="hash",
        is_active=True,
        is_verified=True,
    )
    memory_db_session.add(user)

    # Create wallet with 10000 tokens
    wallet = EmployeeTokenWallet(
        id=uuid.uuid4(),
        user_id=user.id,
        daily_token_limit=10000,
        available_tokens=10000,
        carry_forward_tokens=0,
        bonus_tokens=0,
        total_tokens_used_today=0,
        last_reset_date=datetime.now(timezone.utc).date()
    )
    memory_db_session.add(wallet)

    # Create OpenAI provider
    provider = AIProvider(
        id=uuid.uuid4(),
        code="OPENAI",
        name="OpenAI",
        is_active=True
    )
    memory_db_session.add(provider)

    # Create test model
    model = AIModel(
        id=uuid.uuid4(),
        provider_id=provider.id,
        code="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        input_token_price=Decimal("0.5"),
        output_token_price=Decimal("1.5"),
        is_active=True,
    )
    memory_db_session.add(model)
    
    # Set default model
    setting = SystemSetting(
        id=uuid.uuid4(),
        setting_key="default_model_id",
        setting_value=str(model.id)
    )
    memory_db_session.add(setting)

    from app.main import app
    from app.api.deps import get_db, get_current_user
    app.dependency_overrides[get_db] = lambda: memory_db_session
    
    async def mock_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    return {"user": user, "wallet": wallet, "provider": provider, "model": model}

def get_auth_headers(client, user):
    """Mock auth headers. Real tests use actual auth flow, but we simulate token for unit testing if auth is disabled or we create a token directly."""
    # Assuming tests/conftest.py provides token generator or we use test bypass
    from app.utils.security import create_access_token
    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_successful_openai_request(
    client: TestClient, memory_db_session: AsyncSession, setup_chat_test_data
):
    user = setup_chat_test_data["user"]
    model = setup_chat_test_data["model"]
    wallet = setup_chat_test_data["wallet"]
    
    # Refresh wallet state
    memory_db_session.add(wallet)
    await memory_db_session.refresh(wallet)
    initial_tokens = wallet.available_tokens

    with patch("app.services.ai_gateway.AIGateway.complete", return_value=SUCCESS_GATEWAY_RESULT) as mock_complete:
        from app.utils.security import create_access_token
        token = create_access_token(str(user.id))
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/chat/completions",
            json={"message": "Hello world", "model_id": str(model.id)},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"]["content"] == "This is a real AI response."
        assert data["usage"]["total_tokens"] == 30
        
        # Verify Wallet deduction
        await memory_db_session.refresh(wallet)
        assert wallet.available_tokens == initial_tokens - 30
        assert wallet.total_tokens_used_today == 30
        
        # Verify Token Transaction
        from sqlalchemy import select
        tx = (await memory_db_session.execute(select(TokenTransaction).where(TokenTransaction.user_id == user.id))).scalar_one()
        assert tx.tokens == 30
        assert tx.transaction_action == "DEBIT"
        
        # Verify Prompt Log & Token Usage
        prompt_log = (await memory_db_session.execute(select(PromptLog).where(PromptLog.user_id == user.id))).scalar_one()
        assert prompt_log.total_tokens == 30
        
        token_usage = (await memory_db_session.execute(select(TokenUsage).where(TokenUsage.user_id == user.id))).scalar_one()
        assert token_usage.total_tokens == 30

@pytest.mark.asyncio
async def test_failed_provider_does_not_deduct_tokens(
    client: TestClient, memory_db_session: AsyncSession, setup_chat_test_data
):
    user = setup_chat_test_data["user"]
    wallet = setup_chat_test_data["wallet"]
    
    await memory_db_session.refresh(wallet)
    initial_tokens = wallet.available_tokens

    with patch("app.services.ai_gateway.AIGateway.complete", side_effect=Exception("Provider timeout")) as mock_complete:
        from app.utils.security import create_access_token
        token = create_access_token(str(user.id))
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/v1/chat/completions",
            json={"message": "Hello world", "model_id": str(setup_chat_test_data["model"].id)},
            headers=headers
        )
        
        assert response.status_code == 502
        
        # Wallet should be unchanged
        await memory_db_session.refresh(wallet)
        assert wallet.available_tokens == initial_tokens
        
        # Audit Log should record FAILED
        from sqlalchemy import select
        audit_log = (await memory_db_session.execute(select(AuditLog).where(AuditLog.action == "CHAT_COMPLETION"))).scalars().all()
        assert any("FAILED" in log.description for log in audit_log)

@pytest.mark.asyncio
async def test_insufficient_wallet(
    client: TestClient, memory_db_session: AsyncSession, setup_chat_test_data
):
    user = setup_chat_test_data["user"]
    wallet = setup_chat_test_data["wallet"]
    
    # Set wallet to 0
    wallet.available_tokens = 0
    memory_db_session.add(wallet)
    await memory_db_session.commit()

    from app.utils.security import create_access_token
    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/v1/chat/completions",
        json={"message": "Hello world", "model_id": str(setup_chat_test_data["model"].id)},
        headers=headers
    )
    
    assert response.status_code == 402
    assert response.json()["detail"]["code"] == "INSUFFICIENT_TOKENS"
