"""
Database-level unit tests for Role and Department models.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from app.models.department import Department
from app.models.role import Role
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_role_db_operations(memory_db_session: AsyncSession):
    """Test Role model database operations (1-9)."""
    # 1 & 2. Create valid role and verify code is stored correctly
    role = Role(
        code="SUPER_ADMIN",
        name="Super Administrator",
        description="Full access role",
    )
    memory_db_session.add(role)
    await memory_db_session.commit()
    await memory_db_session.refresh(role)

    assert role.id is not None
    assert role.code == "SUPER_ADMIN"
    assert role.name == "Super Administrator"

    # 4 & 5. Verify required fields defaults and active status
    assert role.is_active is True

    # 6. Verify timestamp behavior
    assert isinstance(role.created_at, datetime)
    assert isinstance(role.updated_at, datetime)

    # 7. Retrieve role by code
    query = select(Role).where(Role.code == "SUPER_ADMIN")
    res = await memory_db_session.execute(query)
    fetched = res.scalar_one_or_none()
    assert fetched is not None
    assert fetched.id == role.id

    # 8. Update role
    role.name = "Root Admin"
    await memory_db_session.commit()
    await memory_db_session.refresh(role)
    assert role.name == "Root Admin"

    # 9. Deactivate role
    role.is_active = False
    await memory_db_session.commit()
    await memory_db_session.refresh(role)
    assert role.is_active is False


@pytest.mark.asyncio
async def test_department_db_operations(memory_db_session: AsyncSession):
    """Test Department model database operations (1-9)."""
    # 1 & 2. Create valid department and verify code is stored correctly
    dept = Department(
        code="FINANCE",
        name="Finance & Audits",
        description="Handles budgeting",
    )
    memory_db_session.add(dept)
    await memory_db_session.commit()
    await memory_db_session.refresh(dept)

    assert dept.id is not None
    assert dept.code == "FINANCE"
    assert dept.name == "Finance & Audits"

    # 4 & 5. Verify required fields defaults and active status
    assert dept.is_active is True

    # 6. Verify timestamp behavior
    assert isinstance(dept.created_at, datetime)
    assert isinstance(dept.updated_at, datetime)

    # 7. Retrieve department by code
    query = select(Department).where(Department.code == "FINANCE")
    res = await memory_db_session.execute(query)
    fetched = res.scalar_one_or_none()
    assert fetched is not None
    assert fetched.id == dept.id

    # 8. Update department
    dept.name = "Audit & Finance"
    await memory_db_session.commit()
    await memory_db_session.refresh(dept)
    assert dept.name == "Audit & Finance"

    # 9. Deactivate department
    dept.is_active = False
    await memory_db_session.commit()
    await memory_db_session.refresh(dept)
    assert dept.is_active is False


@pytest.mark.asyncio
async def test_db_integrity_uniqueness_and_transactions(
    memory_db_session: AsyncSession,
):

    """Test uniqueness constraints and transaction rollback (10-12)."""
    # 10. Duplicate role code is rejected
    role1 = Role(code="ADMIN", name="Administrator")
    role2 = Role(code="ADMIN", name="Second Admin")
    memory_db_session.add(role1)
    await memory_db_session.commit()

    memory_db_session.add(role2)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 11. Duplicate department code is rejected
    dept1 = Department(code="HR", name="Human Resources")
    dept2 = Department(code="HR", name="Second HR")
    memory_db_session.add(dept1)
    await memory_db_session.commit()

    memory_db_session.add(dept2)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 12. Transaction rollback works
    role_fail = Role(code="ADMIN", name="Fails")  # Duplicate code
    role_ok = Role(code="SALES", name="Sales")
    memory_db_session.add_all([role_fail, role_ok])
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # Verify that the OK one was also rolled back and not saved
    query = select(Role).where(Role.code == "SALES")
    res = await memory_db_session.execute(query)
    assert res.scalar_one_or_none() is None
