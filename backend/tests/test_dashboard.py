"""
Test the Dashboard API.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.services.dashboard import DashboardService
from app.models.user import User
from app.models.department import Department
from app.models.role import Role
from app.models.session import ChatSession
from app.models.prompt_log import PromptLog
from app.models.usage import TokenUsage
from app.models.ai_model import AIModel
from app.models.ai_provider import AIProvider
from app.models.message import ChatMessage

@pytest.fixture
async def setup_data(memory_db_session: AsyncSession):
    # Provide basic structure
    provider = AIProvider(id=uuid.uuid4(), code="OPENAI", name="OpenAI")
    model = AIModel(id=uuid.uuid4(), code="GPT4", name="GPT-4", provider_id=provider.id,
                    max_context_tokens=8000, max_output_tokens=4000, 
                    input_token_price=Decimal("0.03"), output_token_price=Decimal("0.06"))
    
    dept_eng = Department(id=uuid.uuid4(), code="ENG", name="Engineering", is_active=True)
    dept_sales = Department(id=uuid.uuid4(), code="SALES", name="Sales", is_active=True)
    
    # Fetch roles created in conftest
    result = await memory_db_session.execute(select(Role))
    roles = result.scalars().all()
    role_map = {r.code: r for r in roles}
    sa_role = role_map["SUPER_ADMIN"]
    mgr_role = role_map["MANAGER"]
    emp_role = role_map["EMPLOYEE"]
    viewer_role = role_map["VIEWER"]
    
    memory_db_session.add_all([provider, model, dept_eng, dept_sales])
    
    u_sa = User(id=uuid.uuid4(), employee_code="SA1", email="sa@ex.com", full_name="SA", password_hash="hash", role=sa_role, is_active=True)
    
    u_mgr_eng = User(id=uuid.uuid4(), employee_code="MGR1", email="mgr@ex.com", full_name="Mgr", password_hash="hash", role=mgr_role, department_id=dept_eng.id, is_active=True)
    u_emp_eng = User(id=uuid.uuid4(), employee_code="EMP1", email="emp1@ex.com", full_name="Emp 1", password_hash="hash", role=emp_role, department_id=dept_eng.id, is_active=True)
    
    u_emp_sales = User(id=uuid.uuid4(), employee_code="EMP2", email="emp2@ex.com", full_name="Emp 2", password_hash="hash", role=emp_role, department_id=dept_sales.id, is_active=True)
    u_viewer = User(id=uuid.uuid4(), employee_code="VIEW1", email="v@ex.com", full_name="Viewer", password_hash="hash", role=viewer_role, is_active=True)
    
    memory_db_session.add_all([u_sa, u_mgr_eng, u_emp_eng, u_emp_sales, u_viewer])
    
    # Session & Usage for ENG employee
    session1 = ChatSession(id=uuid.uuid4(), user_id=u_emp_eng.id, model_id=model.id, started_at=datetime.now(timezone.utc))
    msg1 = ChatMessage(id=uuid.uuid4(), session_id=session1.id, sender_type="user", message_type="text", message_content="hello", message_order=1)
    log1 = PromptLog(id=uuid.uuid4(), session_id=session1.id, user_id=u_emp_eng.id, model_id=model.id, message_id=msg1.id, prompt_text="hello", response_text="world", prompt_hash="hash", input_tokens=10, output_tokens=20, total_tokens=30, response_time_ms=100, created_at=datetime.now(timezone.utc))
    usage1 = TokenUsage(id=uuid.uuid4(), user_id=u_emp_eng.id, session_id=session1.id, prompt_log_id=log1.id, model_id=model.id,
                        input_tokens=10, output_tokens=20, total_tokens=30,
                        input_cost=Decimal("0.1"), output_cost=Decimal("0.2"), total_cost=Decimal("0.3"),
                        usage_date=datetime.now(timezone.utc).date())
                        
    # Session & Usage for SALES employee
    session2 = ChatSession(id=uuid.uuid4(), user_id=u_emp_sales.id, model_id=model.id, started_at=datetime.now(timezone.utc))
    msg2 = ChatMessage(id=uuid.uuid4(), session_id=session2.id, sender_type="user", message_type="text", message_content="hello", message_order=1)
    log2 = PromptLog(id=uuid.uuid4(), session_id=session2.id, user_id=u_emp_sales.id, model_id=model.id, message_id=msg2.id, prompt_text="hello", response_text="world", prompt_hash="hash", input_tokens=5, output_tokens=5, total_tokens=10, response_time_ms=100, created_at=datetime.now(timezone.utc))
    usage2 = TokenUsage(id=uuid.uuid4(), user_id=u_emp_sales.id, session_id=session2.id, prompt_log_id=log2.id, model_id=model.id,
                        input_tokens=5, output_tokens=5, total_tokens=10,
                        input_cost=Decimal("0.05"), output_cost=Decimal("0.05"), total_cost=Decimal("0.1"),
                        usage_date=datetime.now(timezone.utc).date())
    
    memory_db_session.add_all([session1, msg1, log1, usage1, session2, msg2, log2, usage2])
    await memory_db_session.commit()
    
    return {
        "u_sa": u_sa,
        "u_mgr_eng": u_mgr_eng,
        "u_emp_eng": u_emp_eng,
        "u_emp_sales": u_emp_sales,
        "u_viewer": u_viewer
    }


@pytest.mark.asyncio
async def test_dashboard_super_admin(memory_db_session: AsyncSession, setup_data):
    res = await DashboardService.get_overview(memory_db_session, setup_data["u_sa"])
    assert res.role == "SUPER_ADMIN"
    assert res.scope == "PLATFORM"
    assert res.users.total >= 5
    assert res.departments.total == 2
    assert res.conversations.total == 2
    assert res.ai_requests.total == 2
    assert res.tokens.total == 40
    assert res.cost.estimated_total == 0.4


@pytest.mark.asyncio
async def test_dashboard_manager(memory_db_session: AsyncSession, setup_data):
    res = await DashboardService.get_overview(memory_db_session, setup_data["u_mgr_eng"])
    assert res.role == "MANAGER"
    assert res.scope == "DEPARTMENT"
    assert res.users.total == 2 # mgr + emp_eng
    assert res.conversations.total == 1
    assert res.ai_requests.total == 1
    assert res.tokens.total == 30
    assert res.cost.estimated_total == 0.3


@pytest.mark.asyncio
async def test_dashboard_employee(memory_db_session: AsyncSession, setup_data):
    res = await DashboardService.get_overview(memory_db_session, setup_data["u_emp_eng"])
    assert res.role == "EMPLOYEE"
    assert res.scope == "PERSONAL"
    assert res.conversations.total == 1
    assert res.ai_requests.total == 1
    assert res.tokens.total == 30
    assert res.cost.estimated_total == 0.3


@pytest.mark.asyncio
async def test_dashboard_viewer(memory_db_session: AsyncSession, setup_data):
    res = await DashboardService.get_overview(memory_db_session, setup_data["u_viewer"])
    assert res.role == "VIEWER"
    assert res.scope == "READONLY"
    assert res.users is None
    assert res.conversations is None
