"""
Database-level unit tests for Permission and junction models.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions


@pytest.mark.asyncio
async def test_permission_db_operations(memory_db_session: AsyncSession):
    """Test basic Permission model database operations."""
    perm = Permission(
        code="user.create",
        name="Create Users",
        description="Allows creating new organization users",
        resource="user",
        action="create",
    )
    memory_db_session.add(perm)
    await memory_db_session.commit()
    await memory_db_session.refresh(perm)

    assert perm.id is not None
    assert perm.code == "user.create"
    assert perm.name == "Create Users"
    assert perm.resource == "user"
    assert perm.action == "create"
    assert perm.is_active is True
    assert isinstance(perm.created_at, datetime)
    assert isinstance(perm.updated_at, datetime)

    # Unique code constraint
    dup_perm = Permission(
        code="user.create",
        name="Dup Create",
        resource="user",
        action="create",
    )
    memory_db_session.add(dup_perm)
    with pytest.raises(IntegrityError):
        await memory_db_session.commit()
    await memory_db_session.rollback()


@pytest.mark.asyncio
async def test_role_permission_many_to_many(memory_db_session: AsyncSession):
    """Test many-to-many relationship between Role and Permission."""
    role = Role(code="ADMIN", name="Administrator")
    perm1 = Permission(
        code="user.create", name="Create Users", resource="user", action="create"
    )
    perm2 = Permission(
        code="user.read", name="Read Users", resource="user", action="read"
    )

    # Associate permissions with role before first commit
    role.permissions = [perm1, perm2]

    memory_db_session.add_all([role, perm1, perm2])
    await memory_db_session.commit()

    role_id = role.id
    perm1_id = perm1.id
    perm2_id = perm2.id


    # Query back and verify association
    query = (
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permissions))
    )
    res = await memory_db_session.execute(query)
    fetched_role = res.scalar_one()
    assert len(fetched_role.permissions) == 2
    assert any(p.id == perm1_id for p in fetched_role.permissions)
    assert any(p.id == perm2_id for p in fetched_role.permissions)

    # 1. Test duplicate assignment is rejected at DB level
    from sqlalchemy import insert
    stmt = insert(role_permissions).values(role_id=role_id, permission_id=perm1_id)
    with pytest.raises(IntegrityError):
        await memory_db_session.execute(stmt)
        await memory_db_session.commit()
    await memory_db_session.rollback()

    # 2. Test permission removal
    # Re-query to avoid expired state or session issues
    query_req = (
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permissions))
    )
    res_req = await memory_db_session.execute(query_req)
    role_to_remove = res_req.scalar_one()
    role_to_remove.permissions = [
        p for p in role_to_remove.permissions if p.id != perm1_id
    ]
    await memory_db_session.commit()

    # Verify only 1 permission remains
    res_verify = await memory_db_session.execute(query_req)
    role_verified = res_verify.scalar_one()
    assert len(role_verified.permissions) == 1
    assert role_verified.permissions[0].id == perm2_id

    # 3. Deleting a Role does NOT delete the Permission, only the association
    await memory_db_session.delete(role_verified)
    await memory_db_session.commit()

    # Verify Permission still exists
    perm_query = select(Permission).where(Permission.id == perm1_id)
    perm_res = await memory_db_session.execute(perm_query)
    assert perm_res.scalar_one_or_none() is not None

    # Verify junction table record is gone
    j_query = select(role_permissions).where(
        role_permissions.c.permission_id == perm1_id
    )
    j_res = await memory_db_session.execute(j_query)
    assert len(j_res.all()) == 0
