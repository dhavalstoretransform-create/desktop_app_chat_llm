"""
Tests for Step 2 — Database Architecture layer separation.

Verifies:
  1. BaseModel mixins (UUIDMixin, TimestampMixin).
  2. BaseRepository CRUD functionality.
  3. BaseService business delegation.
  4. Layer isolation (Database -> Session -> Repository -> Service -> API).
"""

from __future__ import annotations

import uuid
from datetime import datetime

import pytest
from app.models.base import BaseModel
from app.repositories.base import BaseRepository
from app.services.base import BaseService
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


# ── Concrete test model ───────────────────────────────────────────────────────
class SampleItem(BaseModel):
    """Concrete ORM model used strictly for testing database architecture."""

    __tablename__ = "test_sample_items"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class SampleItemRepository(BaseRepository[SampleItem]):
    """Concrete repository for testing."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(model=SampleItem, db=db)


class SampleItemService(BaseService[SampleItem, SampleItemRepository]):
    """Concrete service for testing."""

    def __init__(self, repository: SampleItemRepository) -> None:
        super().__init__(repository=repository)



class TestDatabaseArchitecture:
    """Test suite for database architecture patterns."""

    @pytest.mark.asyncio
    async def test_base_model_mixins(self, memory_db_session: AsyncSession):
        """Test UUID primary key and UTC timestamp mixins."""
        item = SampleItem(name="Test Widget", description="A test item")
        memory_db_session.add(item)
        await memory_db_session.commit()
        await memory_db_session.refresh(item)

        assert isinstance(item.id, uuid.UUID)
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)
        assert item.name == "Test Widget"
        assert repr(item).startswith("<SampleItem(")

    @pytest.mark.asyncio
    async def test_base_repository_crud(self, memory_db_session: AsyncSession):
        """Test BaseRepository CRUD operations."""
        repo = SampleItemRepository(db=memory_db_session)

        # Create
        created = await repo.create(obj_in={"name": "Item 1", "description": "Desc 1"})
        assert created.id is not None
        assert created.name == "Item 1"

        # Read (get by ID)
        fetched = await repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Item 1"

        # Count
        count = await repo.count()
        assert count == 1

        # Read multi (get_multi)
        items = await repo.get_multi(skip=0, limit=10)
        assert len(items) == 1
        assert items[0].id == created.id

        # Update
        updated = await repo.update(db_obj=created, obj_in={"name": "Updated Item 1"})
        assert updated.name == "Updated Item 1"

        # Delete
        deleted = await repo.delete(id=created.id)
        assert deleted is not None
        assert deleted.id == created.id

        # Verify deletion
        assert await repo.get(created.id) is None
        assert await repo.count() == 0

    @pytest.mark.asyncio
    async def test_base_service_delegation(self, memory_db_session: AsyncSession):
        """Test BaseService delegation to repository."""
        repo = SampleItemRepository(db=memory_db_session)
        service = SampleItemService(repository=repo)

        # Create via service
        item = await service.create(
            obj_in={"name": "Service Item", "description": "Via Service"}
        )
        assert item.name == "Service Item"

        # Get via service
        fetched = await service.get(item.id)
        assert fetched is not None
        assert fetched.name == "Service Item"

        # Count via service
        assert await service.count() == 1

        # Update via service
        updated = await service.update(
            id=item.id, obj_in={"name": "Updated via Service"}
        )
        assert updated is not None
        assert updated.name == "Updated via Service"

        # Delete via service
        deleted = await service.delete(id=item.id)
        assert deleted is not None
        assert await service.count() == 0

    @pytest.mark.asyncio
    async def test_all_domain_models_orm(self, memory_db_session: AsyncSession):
        """Verify that all new domain models can be instantiated and saved."""
        from app.models.audit import AuditLog
        from app.models.department import Department
        from app.models.role import Role
        from app.models.setting import SystemSetting
        from app.models.user import User
        from app.models.wallet import EmployeeTokenWallet

        # Create Department
        dept = Department(code="FIN", name="Finance", description="Finance Dept")
        # Create Role
        role = Role(code="ANALYST", name="Analyst", description="Analyst Role")
        memory_db_session.add_all([dept, role])
        await memory_db_session.commit()


        # Create User
        user = User(
            employee_code="EMP_001",
            full_name="John Doe",
            email="john@example.com",
            password_hash="hashed_pw",
            role_id=role.id,
            department_id=dept.id,
        )
        memory_db_session.add(user)
        await memory_db_session.commit()

        # Create Wallet
        wallet = EmployeeTokenWallet(
            user_id=user.id,
            daily_token_limit=5000,
            available_tokens=5000,
        )
        # Create Setting
        setting = SystemSetting(
            setting_key="max_daily_budget",
            setting_value="100000",
        )
        # Create AuditLog
        audit = AuditLog(
            user_id=user.id,
            action="CREATE",
            entity_name="user",
            entity_id=user.id,
        )
        memory_db_session.add_all([wallet, setting, audit])
        await memory_db_session.commit()

        assert dept.id is not None
        assert role.id is not None
        assert user.id is not None
        assert wallet.id is not None
        assert setting.id is not None
        assert audit.id is not None

