"""
Database-level unit tests for User / Employee models.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from app.models.department import Department
from app.models.role import Role
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_user_db_operations(memory_db_session: AsyncSession):
    """Test User model database operations (CRUD & deactivation)."""
    # Create required Role and Department first
    role = Role(code="STAFF", name="Staff Member")
    dept = Department(code="SALES", name="Sales Department")
    memory_db_session.add_all([role, dept])
    await memory_db_session.commit()

    # 1. Create a valid user
    user = User(
        employee_code="EMP_101",
        full_name="Alice Smith",
        email="alice@example.com",
        password_hash="hashedpassword123",
        role_id=role.id,
        department_id=dept.id,
    )
    memory_db_session.add(user)
    await memory_db_session.commit()
    await memory_db_session.refresh(user)

    assert user.id is not None
    assert user.employee_code == "EMP_101"
    assert user.full_name == "Alice Smith"
    assert user.email == "alice@example.com"
    assert user.role_id == role.id
    assert user.department_id == dept.id
    assert user.is_active is True
    assert user.is_verified is False
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

    # 2. Retrieve user by email
    query = select(User).where(User.email == "alice@example.com")
    res = await memory_db_session.execute(query)
    fetched = res.scalar_one_or_none()
    assert fetched is not None
    assert fetched.id == user.id

    # 3. Retrieve user by employee code
    query = select(User).where(User.employee_code == "EMP_101")
    res = await memory_db_session.execute(query)
    fetched_code = res.scalar_one_or_none()
    assert fetched_code is not None
    assert fetched_code.id == user.id

    # 4. Update user details
    user.full_name = "Alice Jones"
    await memory_db_session.commit()
    await memory_db_session.refresh(user)
    assert user.full_name == "Alice Jones"

    # 5. Soft delete / deactivate user
    user.is_active = False
    await memory_db_session.commit()
    await memory_db_session.refresh(user)
    assert user.is_active is False


@pytest.mark.asyncio
async def test_user_db_integrity_violations(memory_db_session: AsyncSession):
    """Test database-level uniqueness constraints for User."""
    role = Role(code="DEV", name="Developer")
    dept = Department(code="ENG", name="Engineering")
    memory_db_session.add_all([role, dept])
    await memory_db_session.commit()
    
    role_id = role.id
    dept_id = dept.id

    user1 = User(
        employee_code="EMP_001",
        full_name="User One",
        email="one@example.com",
        password_hash="pw1",
        role_id=role_id,
        department_id=dept_id,
    )
    memory_db_session.add(user1)
    await memory_db_session.commit()

    # 1. Duplicate email is rejected
    user_dup_email = User(
        employee_code="EMP_002",
        full_name="User Two",
        email="one@example.com",  # Duplicate email
        password_hash="pw2",
        role_id=role_id,
        department_id=dept_id,
    )
    memory_db_session.add(user_dup_email)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 2. Duplicate employee code is rejected
    user_dup_code = User(
        employee_code="EMP_001",  # Duplicate code
        full_name="User Three",
        email="three@example.com",
        password_hash="pw3",
        role_id=role_id,
        department_id=dept_id,
    )

    memory_db_session.add(user_dup_code)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()


@pytest.mark.asyncio
async def test_role_and_department_deletion_protection(
    memory_db_session: AsyncSession,
):
    """Test that Roles and Departments cannot be deleted if referenced by a User."""
    role = Role(code="PROTECTED_ROLE", name="Protected Role")
    dept = Department(code="PROTECTED_DEPT", name="Protected Department")
    memory_db_session.add_all([role, dept])
    await memory_db_session.commit()

    role_id = role.id
    dept_id = dept.id

    user = User(
        employee_code="EMP_999",
        full_name="Protected User",
        email="protected@example.com",
        password_hash="pw",
        role_id=role_id,
        department_id=dept_id,
    )
    memory_db_session.add(user)
    await memory_db_session.commit()

    # Try to delete Role
    await memory_db_session.delete(role)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # Try to delete Department
    await memory_db_session.delete(dept)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()

