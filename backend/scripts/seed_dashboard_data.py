import asyncio
import os
import sys
import uuid
import random
import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.models.prompt_log import PromptLog
from app.models.usage import TokenUsage
from app.models.wallet import EmployeeTokenWallet
from app.models.token_transaction import TokenTransaction
from app.models.audit import AuditLog
from app.models.ai_model import AIModel
from app.utils.security import hash_password

TEST_EMAIL_PREFIX = "dashboard."

ROLES_CONFIG = [
    {"code": "SUPER_ADMIN", "name": "Super Admin"},
    {"code": "ADMIN", "name": "Admin"},
    {"code": "MANAGER", "name": "Manager"},
    {"code": "EMPLOYEE", "name": "Employee"},
    {"code": "VIEWER", "name": "Viewer"},
]

DEPARTMENTS_CONFIG = [
    {"code": "ENG", "name": "Engineering"},
    {"code": "MKT", "name": "Marketing"},
    {"code": "SAL", "name": "Sales"},
    {"code": "FIN", "name": "Finance"},
    {"code": "HR", "name": "HR"},
    {"code": "SUP", "name": "Support"},
]

TEST_USERS = [
    {"email": "dashboard.admin@test.com", "role": "ADMIN", "dept": "ENG", "tokens": 100000, "name": "Test Admin"},
    {"email": "dashboard.manager.it@test.com", "role": "MANAGER", "dept": "ENG", "tokens": 50000, "name": "Test Manager IT"},
    {"email": "dashboard.manager.sales@test.com", "role": "MANAGER", "dept": "SAL", "tokens": 50000, "name": "Test Manager Sales"},
    {"email": "dashboard.employee1@test.com", "role": "EMPLOYEE", "dept": "ENG", "tokens": 20000, "name": "Test Emp 1"},
    {"email": "dashboard.employee2@test.com", "role": "EMPLOYEE", "dept": "ENG", "tokens": 15000, "name": "Test Emp 2"},
    {"email": "dashboard.employee3@test.com", "role": "EMPLOYEE", "dept": "SAL", "tokens": 30000, "name": "Test Emp 3"},
    {"email": "dashboard.employee4@test.com", "role": "EMPLOYEE", "dept": "MKT", "tokens": 10000, "name": "Test Emp 4"},
    {"email": "dashboard.employee5@test.com", "role": "EMPLOYEE", "dept": "HR", "tokens": 25000, "name": "Test Emp 5"},
    {"email": "dashboard.viewer1@test.com", "role": "VIEWER", "dept": "SUP", "tokens": 5000, "name": "Test Viewer 1"},
    {"email": "dashboard.viewer2@test.com", "role": "VIEWER", "dept": "FIN", "tokens": 5000, "name": "Test Viewer 2"},
]

async def get_or_create_roles(session: AsyncSession):
    roles = {}
    for r in ROLES_CONFIG:
        stmt = select(Role).where(Role.code == r["code"])
        role = (await session.execute(stmt)).scalar_one_or_none()
        if not role:
            role = Role(id=uuid.uuid4(), code=r["code"], name=r["name"], is_active=True)
            session.add(role)
            await session.commit()
            await session.refresh(role)
        roles[r["code"]] = role
    return roles

async def get_or_create_departments(session: AsyncSession):
    depts = {}
    for d in DEPARTMENTS_CONFIG:
        stmt = select(Department).where(Department.code == d["code"])
        dept = (await session.execute(stmt)).scalar_one_or_none()
        if not dept:
            dept = Department(id=uuid.uuid4(), code=d["code"], name=d["name"], is_active=True)
            session.add(dept)
            await session.commit()
            await session.refresh(dept)
        depts[d["code"]] = dept
    return depts

async def seed_data():
    async with AsyncSessionLocal() as session:
        try:
            print("Fetching/Creating dependencies (Roles, Departments)...")
            roles = await get_or_create_roles(session)
            depts = await get_or_create_departments(session)
            
            stmt = select(AIModel).where(AIModel.is_active == True)
            models = (await session.execute(stmt)).scalars().all()
            if not models:
                print("Error: No active AI Models found. Please run regular migrations/seed first.")
                return
                
            print(f"Found {len(models)} active AI Models.")
            
            print("Creating test users...")
            created_users = []
            for tu in TEST_USERS:
                stmt = select(User).where(User.email == tu["email"])
                existing = (await session.execute(stmt)).scalar_one_or_none()
                if existing:
                    created_users.append(existing)
                    continue
                
                user_id = uuid.uuid4()
                user = User(
                    id=user_id,
                    employee_code=f"DASH-{len(created_users)+1:03d}",
                    full_name=tu["name"],
                    email=tu["email"],
                    password_hash=hash_password("securepassword"),
                    role_id=roles[tu["role"]].id,
                    department_id=depts[tu["dept"]].id,
                    is_verified=True,
                    is_active=True
                )
                session.add(user)
                created_users.append(user)
                
                # Wallet
                wallet = EmployeeTokenWallet(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    daily_token_limit=100000,
                    carry_forward_tokens=0,
                    bonus_tokens=0,
                    available_tokens=tu["tokens"],
                    total_tokens_used_today=0,
                    last_reset_date=datetime.now(timezone.utc).date()
                )
                session.add(wallet)
                
            await session.commit()
            print(f"Verified {len(created_users)} test users.")
            
            print("Generating conversations, messages, requests, and usage...")
            convs_created = 0
            msgs_created = 0
            reqs_created = 0
            
            now = datetime.now(timezone.utc)
            
            # Generate Audit Log for user creation just to have data
            for u in created_users:
                log_time = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                audit = AuditLog(
                    id=uuid.uuid4(),
                    user_id=u.id,
                    action="USER_CREATED",
                    entity_name="User",
                    entity_id=u.id,
                    description="Seed Dashboard User",
                    created_at=log_time,
                    updated_at=log_time
                )
                session.add(audit)
                
                audit2 = AuditLog(
                    id=uuid.uuid4(),
                    user_id=u.id,
                    action="LOGIN",
                    entity_name="Auth",
                    description="User logged in",
                    created_at=log_time + timedelta(minutes=5),
                    updated_at=log_time + timedelta(minutes=5)
                )
                session.add(audit2)

            for user in created_users:
                num_convs = random.randint(2, 4)
                for _ in range(num_convs):
                    model = random.choice(models)
                    conv_time = now - timedelta(days=random.randint(0, 6), hours=random.randint(1, 23))
                    
                    conv = ChatSession(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        model_id=model.id,
                        session_title=f"Dashboard Test {uuid.uuid4().hex[:4]}",
                        session_status="active",
                        total_messages=0,
                        total_input_tokens=0,
                        total_output_tokens=0,
                        started_at=conv_time,
                        created_at=conv_time,
                        updated_at=conv_time
                    )
                    session.add(conv)
                    await session.flush()
                    convs_created += 1
                    
                    num_reqs = random.randint(2, 5)
                    for r_idx in range(num_reqs):
                        msg_time = conv_time + timedelta(minutes=r_idx*2)
                        
                        input_tok = random.randint(50, 800)
                        output_tok = random.randint(100, 1500)
                        total_tok = input_tok + output_tok
                        
                        input_cost = (Decimal(str(input_tok)) * (model.input_token_price or Decimal("0"))) / Decimal("1000000")
                        output_cost = (Decimal(str(output_tok)) * (model.output_token_price or Decimal("0"))) / Decimal("1000000")
                        tot_cost = input_cost + output_cost
                        
                        # User Msg
                        u_msg = ChatMessage(
                            id=uuid.uuid4(),
                            session_id=conv.id,
                            sender_type="user",
                            message_type="text",
                            message_content=f"Tell me about {random.choice(['AI', 'weather', 'finance', 'history'])}",
                            input_tokens=0,
                            output_tokens=0,
                            message_order=r_idx*2 + 1,
                            created_at=msg_time,
                            updated_at=msg_time
                        )
                        session.add(u_msg)
                        
                        # Assistant Msg
                        a_msg = ChatMessage(
                            id=uuid.uuid4(),
                            session_id=conv.id,
                            sender_type="assistant",
                            message_type="text",
                            message_content=f"Here is information regarding your query...",
                            input_tokens=input_tok,
                            output_tokens=output_tok,
                            response_time_ms=random.randint(500, 3000),
                            message_order=r_idx*2 + 2,
                            created_at=msg_time + timedelta(seconds=2),
                            updated_at=msg_time + timedelta(seconds=2)
                        )
                        session.add(a_msg)
                        msgs_created += 2
                        
                        # Prompt Log
                        pl = PromptLog(
                            id=uuid.uuid4(),
                            user_id=user.id,
                            session_id=conv.id,
                            message_id=a_msg.id,
                            model_id=model.id,
                            prompt_text=u_msg.message_content,
                            response_text=a_msg.message_content,
                            prompt_hash="dummyhash",
                            input_tokens=input_tok,
                            output_tokens=output_tok,
                            total_tokens=total_tok,
                            status="completed",
                            created_at=msg_time,
                            updated_at=msg_time
                        )
                        session.add(pl)
                        
                        # Token Usage
                        tu = TokenUsage(
                            id=uuid.uuid4(),
                            user_id=user.id,
                            session_id=conv.id,
                            prompt_log_id=pl.id,
                            model_id=model.id,
                            input_tokens=input_tok,
                            output_tokens=output_tok,
                            total_tokens=total_tok,
                            input_cost=input_cost,
                            output_cost=output_cost,
                            total_cost=tot_cost,
                            usage_date=msg_time.date(),
                            created_at=msg_time,
                            updated_at=msg_time
                        )
                        session.add(tu)
                        
                        # Token Transaction
                        tt = TokenTransaction(
                            id=uuid.uuid4(),
                            user_id=user.id,
                            conversation_id=conv.id,
                            model_id=model.id,
                            transaction_type="CHAT_COMPLETION",
                            transaction_action="DEBIT",
                            tokens=total_tok,
                            timestamp=msg_time,
                            created_at=msg_time,
                            updated_at=msg_time
                        )
                        session.add(tt)
                        
                        # Audit Log
                        al = AuditLog(
                            id=uuid.uuid4(),
                            user_id=user.id,
                            action="CHAT_COMPLETION",
                            entity_name="ChatSession",
                            entity_id=conv.id,
                            description="SUCCESS",
                            created_at=msg_time,
                            updated_at=msg_time
                        )
                        session.add(al)
                        
                        reqs_created += 1
                        
                        # Update session aggregates
                        conv.total_messages += 2
                        conv.total_input_tokens += input_tok
                        conv.total_output_tokens += output_tok
                        
            await session.commit()
            
            print("\n=================================")
            print("Dashboard seed completed.")
            print(f"Users created/verified: {len(created_users)}")
            print(f"Departments present: {len(depts)}")
            print(f"Conversations created: {convs_created}")
            print(f"Messages created: {msgs_created}")
            print(f"AI Requests (PromptLogs/Usage/Transactions): {reqs_created}")
            print(f"Audit Logs: {len(created_users) * 2 + reqs_created}")
            print("=================================\n")

        except Exception as e:
            await session.rollback()
            print(f"Error seeding data: {e}")

async def cleanup_data():
    async with AsyncSessionLocal() as session:
        try:
            print("Cleaning up test data...")
            
            # Find test users
            stmt = select(User.id).where(User.email.like(f"{TEST_EMAIL_PREFIX}%"))
            test_user_ids = (await session.execute(stmt)).scalars().all()
            
            if not test_user_ids:
                print("No test users found.")
                return
                
            # Delete in order of dependencies
            await session.execute(delete(TokenTransaction).where(TokenTransaction.user_id.in_(test_user_ids)))
            await session.execute(delete(TokenUsage).where(TokenUsage.user_id.in_(test_user_ids)))
            await session.execute(delete(PromptLog).where(PromptLog.user_id.in_(test_user_ids)))
            
            # Delete messages inside sessions belonging to test users
            stmt_sessions = select(ChatSession.id).where(ChatSession.user_id.in_(test_user_ids))
            session_ids = (await session.execute(stmt_sessions)).scalars().all()
            if session_ids:
                await session.execute(delete(ChatMessage).where(ChatMessage.session_id.in_(session_ids)))
            
            await session.execute(delete(ChatSession).where(ChatSession.user_id.in_(test_user_ids)))
            await session.execute(delete(EmployeeTokenWallet).where(EmployeeTokenWallet.user_id.in_(test_user_ids)))
            await session.execute(delete(AuditLog).where(AuditLog.user_id.in_(test_user_ids)))
            await session.execute(delete(User).where(User.id.in_(test_user_ids)))
            
            await session.commit()
            print(f"Successfully cleaned up data for {len(test_user_ids)} test users.")
        except Exception as e:
            await session.rollback()
            print(f"Error cleaning up data: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Dashboard Test Data")
    parser.add_argument("--cleanup", action="store_true", help="Remove test data")
    args = parser.parse_args()
    
    if args.cleanup:
        asyncio.run(cleanup_data())
    else:
        asyncio.run(seed_data())
