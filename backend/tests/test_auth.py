"""
Integration and database tests for authentication (Phase 3).
"""

from __future__ import annotations

import pytest
from app.api.deps import get_current_user
from app.core.database import get_db
from app.main import app
from app.models.audit import AuditLog
from app.models.department import Department
from app.models.role import Role
from app.models.user import User
from app.utils.security import hash_password
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
def override_db_dependency(memory_db_session: AsyncSession):
    """Override get_db dependency with in-memory SQLite session."""
    async def _get_db_override():
        yield memory_db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(memory_db_session: AsyncSession) -> User:
    """Fixture to create a test user with a hashed password."""
    role = Role(code="STAFF", name="Staff Member")
    dept = Department(code="ENG", name="Engineering")
    memory_db_session.add_all([role, dept])
    await memory_db_session.commit()
    await memory_db_session.refresh(role)
    await memory_db_session.refresh(dept)

    user = User(
        employee_code="EMP_TEST",
        full_name="Alice Tester",
        email="alice@example.com",
        password_hash=hash_password("securepassword"),
        role_id=role.id,
        department_id=dept.id,
    )
    memory_db_session.add(user)
    await memory_db_session.commit()
    await memory_db_session.refresh(user)
    return user


def test_auth_login_success(client: TestClient, test_user: User):
    """Test successful user login and token generation."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert "refresh_token" in res_data
    assert res_data["token_type"] == "bearer"


def test_auth_login_failed_password(client: TestClient, test_user: User):
    """Test failed login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email" in response.json()["detail"]


def test_auth_login_nonexistent_user(client: TestClient):
    """Test login attempt with nonexistent email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "somepassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_audit_log_created(
    client: TestClient, test_user: User, memory_db_session: AsyncSession
):
    """Test that audit log entries are generated for auth actions."""
    # 1. Successful login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # 2. Failed login
    client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "wrongpassword"},
    )

    # 3. Successful refresh
    client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    # 4. Token validation failure (triggering AUTHENTICATION_FAILURE audit)
    import jwt
    bad_sig_jwt = jwt.encode(
        {"sub": str(test_user.id), "type": "access"}, "wrongsecret"
    )
    client.get(
        "/api/v1/auth/test-me",
        headers={"Authorization": f"Bearer {bad_sig_jwt}"},
    )

    query = select(AuditLog).where(AuditLog.user_id == test_user.id)
    res = await memory_db_session.execute(query)
    logs = res.scalars().all()
    assert len(logs) >= 4
    assert any(log.action == "LOGIN_SUCCESS" for log in logs)
    assert any(log.action == "LOGIN_FAILED" for log in logs)
    assert any(log.action == "TOKEN_REFRESH" for log in logs)
    assert any(log.action == "AUTHENTICATION_FAILURE" for log in logs)



def test_auth_refresh_token_cycle(client: TestClient, test_user: User):
    """Test using refresh token to obtain a new access token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    res_data = refresh_res.json()
    assert "access_token" in res_data
    assert res_data["refresh_token"] == refresh_token


def test_auth_logout_invalidates_refresh(client: TestClient, test_user: User):
    """Test that logout revokes refresh token and blocks further refreshes."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Logout
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200

    # Subsequent refresh should fail
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 401


# Define a temporary protected route for testing CurrentUserDep
@app.get("/api/v1/auth/test-me")
def route_test_me(current_user: User = Depends(get_current_user)):  # noqa: B008
    return {"id": str(current_user.id), "email": current_user.email}


def test_protected_route_access(client: TestClient, test_user: User):
    """Test protected route access with valid, invalid, and missing JWTs."""
    # 1. Missing Token
    resp_no_token = client.get("/api/v1/auth/test-me")
    assert resp_no_token.status_code == 401

    # 2. Invalid Token
    resp_bad_token = client.get(
        "/api/v1/auth/test-me",
        headers={"Authorization": "Bearer invalid_jwt_token_value"},
    )
    assert resp_bad_token.status_code == 401

    # 3. Valid Token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    access_token = login_res.json()["access_token"]
    resp_valid = client.get(
        "/api/v1/auth/test-me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp_valid.status_code == 200
    assert resp_valid.json()["email"] == "alice@example.com"


def test_auth_me_endpoint(client: TestClient, test_user: User):
    """Test retrieving current user's profile info from GET /api/v1/auth/me."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    access_token = login_res.json()["access_token"]

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["email"] == "alice@example.com"
    assert res_data["full_name"] == "Alice Tester"
    assert "password_hash" not in res_data


@pytest.mark.asyncio
async def test_auth_login_inactive_user(
    client: TestClient, test_user: User, memory_db_session: AsyncSession
):
    """Test login fails for inactive users."""
    test_user.is_active = False
    memory_db_session.add(test_user)
    await memory_db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    assert response.status_code == 401


def test_auth_login_validation_errors(client: TestClient):
    """Test login validation errors for missing fields and malformed email."""
    # 1. Missing email
    r1 = client.post("/api/v1/auth/login", json={"password": "password"})
    assert r1.status_code == 422

    # 2. Missing password
    r2 = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
    assert r2.status_code == 422

    # 3. Invalid email format
    r3 = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "password"},
    )
    assert r3.status_code == 422


def test_auth_expired_jwt(client: TestClient, test_user: User):
    """Test accessing protected endpoint with an expired JWT access token."""
    from datetime import UTC, datetime, timedelta

    import jwt
    from app.core.config import settings

    expired_payload = {
        "sub": str(test_user.id),
        "type": "access",
        "exp": datetime.now(UTC) - timedelta(minutes=10)
    }
    expired_token = jwt.encode(
        expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401


def test_auth_wrong_token_type(client: TestClient, test_user: User):
    """Test accessing protected endpoint with refresh token instead of access token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    refresh_token = login_res.json()["refresh_token"]

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_nonexistent_authenticated_user(client: TestClient):
    """Test accessing protected route with a token for a nonexistent user."""
    import uuid

    from app.utils.security import create_access_token
    
    access_token = create_access_token(subject=uuid.uuid4())

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_auth_inactive_authenticated_user(
    client: TestClient, test_user: User, memory_db_session: AsyncSession
):
    """Test accessing protected route after the user is deactivated in the database."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    access_token = login_res.json()["access_token"]

    # Deactivate user in DB
    test_user.is_active = False
    memory_db_session.add(test_user)
    await memory_db_session.commit()

    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_auth_expired_refresh_token(
    client: TestClient, test_user: User, memory_db_session: AsyncSession
):
    """Test refreshing tokens using an expired refresh token."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "securepassword"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Manually expire the refresh token in the database
    import hashlib
    from datetime import UTC, datetime, timedelta

    from app.models.user_refresh_token import UserRefreshToken
    
    hashed_token = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    query = select(UserRefreshToken).where(UserRefreshToken.token == hashed_token)
    res = await memory_db_session.execute(query)
    db_token = res.scalar_one()
    
    db_token.expires_at = datetime.now(UTC) - timedelta(days=1)
    memory_db_session.add(db_token)
    await memory_db_session.commit()

    # Attempt to refresh
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 401


@pytest.mark.asyncio
async def test_user_registration_comprehensive(
    client: TestClient, memory_db_session: AsyncSession
):
    """Test user registration API endpoints and downstream login/me validation."""
    import uuid

    # 12. Registration works when database has zero users
    # Clear any users created by fixtures
    from app.models.user import User
    from app.utils.security import verify_password
    from sqlalchemy import delete
    
    await memory_db_session.execute(delete(User))
    await memory_db_session.commit()

    # 1. Successful registration → 201
    register_data = {
        "employee_code": "EMP-PM-001",
        "full_name": "Project Manager",
        "email": "projectmanager@gmail.com",
        "password": "Projectmanager@123"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    res_data = response.json()
    
    # 4. Password is never returned
    assert "password" not in res_data
    assert "password_hash" not in res_data
    assert "access_token" not in res_data
    assert "refresh_token" not in res_data
    
    assert res_data["employee_code"] == "EMP-PM-001"
    assert res_data["full_name"] == "Project Manager"
    assert res_data["email"] == "projectmanager@gmail.com"
    
    # 10. Newly registered user has is_active=True
    assert res_data["is_active"] is True
    # 11. Newly registered user has is_verified=False
    assert res_data["is_verified"] is False
    
    user_id = uuid.UUID(res_data["id"])

    # Verify database state
    query = select(User).where(User.id == user_id)
    res = await memory_db_session.execute(query)
    db_user = res.scalar_one()
    
    # 2. Password is stored as Argon2 hash
    assert db_user.password_hash.startswith("$argon2")
    # 3. Plaintext password is never stored
    assert db_user.password_hash != "Projectmanager@123"
    assert verify_password("Projectmanager@123", db_user.password_hash) is True
    
    # 13. Registration does not create permissions, 14. does not grant admin role
    assert db_user.role_id is None
    assert db_user.department_id is None

    # 5. Duplicate email → 409
    dup_email_data = {
        "employee_code": "EMP-PM-002",
        "full_name": "Another PM",
        "email": "PROJECTMANAGER@gmail.com",  # case-insensitive check
        "password": "Projectmanager@123"
    }
    response_dup_email = client.post("/api/v1/auth/register", json=dup_email_data)
    assert response_dup_email.status_code == 409
    
    # 6. Duplicate employee_code → 409
    dup_code_data = {
        "employee_code": "EMP-PM-001",
        "full_name": "Another PM",
        "email": "another@gmail.com",
        "password": "Projectmanager@123"
    }
    response_dup_code = client.post("/api/v1/auth/register", json=dup_code_data)
    assert response_dup_code.status_code == 409

    # 7. Invalid email → 422
    invalid_email_data = {
        "employee_code": "EMP-PM-003",
        "full_name": "Bad Email",
        "email": "invalid-email-format",
        "password": "Projectmanager@123"
    }
    response_bad_email = client.post("/api/v1/auth/register", json=invalid_email_data)
    assert response_bad_email.status_code == 422

    # 8. Missing required field → 422
    missing_field_data = {
        "employee_code": "EMP-PM-004",
        "email": "missingname@gmail.com",
        "password": "Projectmanager@123"
    }
    response_missing = client.post("/api/v1/auth/register", json=missing_field_data)
    assert response_missing.status_code == 422

    # 9. Short/invalid password → appropriate validation error
    short_pwd_data = {
        "employee_code": "EMP-PM-005",
        "full_name": "Short Password",
        "email": "shortpwd@gmail.com",
        "password": "short"
    }
    response_short = client.post("/api/v1/auth/register", json=short_pwd_data)
    assert response_short.status_code == 422

    # 15. Existing Login API can authenticate the newly registered user
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "projectmanager@gmail.com", "password": "Projectmanager@123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    
    # 4. GET /api/v1/auth/me with Bearer token → 200
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "projectmanager@gmail.com"


@pytest.mark.asyncio
async def test_auth_audit_logging_comprehensive(
    client: TestClient, test_user: User, memory_db_session: AsyncSession
):
    """
    Verify that all authentication events (login, failed login, logout, auth failure)
    map correctly to audit logs.
    """
    from app.models.audit import AuditLog
    from sqlalchemy import delete

    # Clear old audit logs for clean assertions
    await memory_db_session.execute(delete(AuditLog))
    await memory_db_session.commit()

    # 1. Successful login creates LOGIN_SUCCESS
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "securepassword"},
    )
    assert login_res.status_code == 200
    refresh_token = login_res.json()["refresh_token"]

    # Verify LOGIN_SUCCESS
    query_success = select(AuditLog).where(AuditLog.action == "LOGIN_SUCCESS")
    res = await memory_db_session.execute(query_success)
    success_log = res.scalar_one()
    assert success_log.user_id == test_user.id
    assert success_log.description == "User logged in successfully"

    # 2. Wrong password creates LOGIN_FAILED
    login_fail_pwd = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert login_fail_pwd.status_code == 401
    assert login_fail_pwd.json()["detail"] == "Incorrect email or password."

    # Verify LOGIN_FAILED for test_user
    res = await memory_db_session.execute(
        select(AuditLog)
        .where(AuditLog.action == "LOGIN_FAILED")
        .where(AuditLog.user_id == test_user.id)
    )
    failed_log_pwd = res.scalar_one()
    assert failed_log_pwd.description == "Login attempt failed"

    # 3. Existing inactive user creates LOGIN_FAILED
    # Deactivate user
    test_user.is_active = False
    memory_db_session.add(test_user)
    await memory_db_session.commit()

    login_inactive = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "securepassword"},
    )
    assert login_inactive.status_code == 401
    assert login_inactive.json()["detail"] == "Incorrect email or password."

    # Verify LOGIN_FAILED for inactive test_user
    res = await memory_db_session.execute(
        select(AuditLog)
        .where(AuditLog.action == "LOGIN_FAILED")
        .where(AuditLog.user_id == test_user.id)
    )
    failed_logs = res.scalars().all()
    assert len(failed_logs) == 2  # One for wrong password, one for inactive account

    # Reactivate user for subsequent tests
    test_user.is_active = True
    memory_db_session.add(test_user)
    await memory_db_session.commit()

    # 4. Unknown email does not leak account existence
    # (creates LOGIN_FAILED with user_id=None)
    login_fail_email = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"},
    )
    assert login_fail_email.status_code == 401
    assert login_fail_email.json()["detail"] == "Incorrect email or password."

    # Verify LOGIN_FAILED for nonexistent user
    res = await memory_db_session.execute(
        select(AuditLog)
        .where(AuditLog.action == "LOGIN_FAILED")
        .where(AuditLog.user_id.is_(None))
    )
    failed_log_email = res.scalar_one()
    assert failed_log_email.description == "Login attempt failed"

    # 5. Logout creates LOGOUT
    logout_res = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_res.status_code == 200

    res = await memory_db_session.execute(
        select(AuditLog).where(AuditLog.action == "LOGOUT")
    )
    logout_log = res.scalar_one()
    assert logout_log.user_id == test_user.id
    assert logout_log.description == "User logged out successfully"

    # 6. Invalid JWT creates AUTHENTICATION_FAILURE
    import jwt
    expired_jwt = jwt.encode(
        {"sub": str(test_user.id), "type": "access", "exp": 0}, "wrongsecret"
    )
    client.get(
        "/api/v1/auth/test-me",
        headers={"Authorization": f"Bearer {expired_jwt}"},
    )
    res = await memory_db_session.execute(
        select(AuditLog).where(AuditLog.action == "AUTHENTICATION_FAILURE")
    )
    auth_fail_log = res.scalar_one()
    assert auth_fail_log.user_id == test_user.id
    assert auth_fail_log.description == "Authentication validation failed"


@pytest.mark.asyncio
async def test_auth_login_verification_logic(
    client: TestClient, memory_db_session: AsyncSession
):
    """Verify that successful login marks the user as verified, while failed logins keep it false."""
    from app.models.user import User
    from app.utils.security import hash_password

    # Test 1: Create active user that is unverified
    user_unverified = User(
        employee_code="EMP-VER-01",
        full_name="Verification Tester",
        email="verterster@example.com",
        password_hash=hash_password("securepassword123"),
        is_active=True,
        is_verified=False,
    )
    memory_db_session.add(user_unverified)
    await memory_db_session.commit()
    await memory_db_session.refresh(user_unverified)

    # Login successfully
    response_success = client.post(
        "/api/v1/auth/login",
        json={"email": "verterster@example.com", "password": "securepassword123"},
    )
    assert response_success.status_code == 200

    # Assert is_verified == True
    await memory_db_session.refresh(user_unverified)
    assert user_unverified.is_verified is True

    # Test 2: Create another unverified user and login with wrong password
    user_fail = User(
        employee_code="EMP-VER-02",
        full_name="Verification Fail Tester",
        email="verfail@example.com",
        password_hash=hash_password("securepassword123"),
        is_active=True,
        is_verified=False,
    )
    memory_db_session.add(user_fail)
    await memory_db_session.commit()
    await memory_db_session.refresh(user_fail)

    response_fail = client.post(
        "/api/v1/auth/login",
        json={"email": "verfail@example.com", "password": "wrongpassword"},
    )
    assert response_fail.status_code == 401

    # Assert is_verified remains False
    await memory_db_session.refresh(user_fail)
    assert user_fail.is_verified is False

    # Test 3: Create inactive user and login
    user_inactive = User(
        employee_code="EMP-VER-03",
        full_name="Verification Inactive",
        email="verinactive@example.com",
        password_hash=hash_password("securepassword123"),
        is_active=False,
        is_verified=False,
    )
    memory_db_session.add(user_inactive)
    await memory_db_session.commit()
    await memory_db_session.refresh(user_inactive)

    response_inactive = client.post(
        "/api/v1/auth/login",
        json={"email": "verinactive@example.com", "password": "securepassword123"},
    )
    assert response_inactive.status_code == 401

    # Assert is_verified remains unchanged (False)
    await memory_db_session.refresh(user_inactive)
    assert user_inactive.is_verified is False


@pytest.mark.asyncio
async def test_auth_timestamp_and_logout_behavior(
    client: TestClient, memory_db_session: AsyncSession
):
    """
    Verify that login updates last_login_at & is_verified,
    and logout revokes token & does not update last_login_at.
    """
    import hashlib

    from app.models.audit import AuditLog
    from app.models.user import User
    from app.models.user_refresh_token import UserRefreshToken
    from app.utils.security import hash_password

    # Create unverified user with no last_login_at
    user = User(
        employee_code="EMP-TIME-01",
        full_name="Timestamp Tester",
        email="timetester@example.com",
        password_hash=hash_password("securepassword123"),
        is_active=True,
        is_verified=False,
        last_login_at=None,
    )
    memory_db_session.add(user)
    await memory_db_session.commit()
    await memory_db_session.refresh(user)

    # 1. Login successfully
    response_login = client.post(
        "/api/v1/auth/login",
        json={"email": "timetester@example.com", "password": "securepassword123"},
    )
    assert response_login.status_code == 200
    res_data = response_login.json()
    refresh_token = res_data["refresh_token"]

    await memory_db_session.refresh(user)
    # Assert successful login updates last_login_at
    assert user.last_login_at is not None
    last_login_time = user.last_login_at

    # Assert successful login changes is_verified from FALSE to TRUE
    assert user.is_verified is True

    # 2. Logout
    response_logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert response_logout.status_code == 200

    await memory_db_session.refresh(user)
    # Assert logout does NOT modify last_login_at
    assert user.last_login_at == last_login_time

    # Assert logout creates a LOGOUT audit record
    query_logout_audit = select(AuditLog).where(
        AuditLog.action == "LOGOUT",
        AuditLog.user_id == user.id
    )
    res_audit = await memory_db_session.execute(query_logout_audit)
    logout_audit = res_audit.scalar_one_or_none()
    assert logout_audit is not None
    assert logout_audit.description == "User logged out successfully"

    # Assert logout revokes the refresh token
    hashed_token = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    query_token = select(UserRefreshToken).where(UserRefreshToken.token == hashed_token)
    res_token = await memory_db_session.execute(query_token)
    db_token = res_token.scalar_one()
    assert db_token.is_revoked is True


@pytest.mark.asyncio
async def test_auth_logout_timestamp_regression(
    client: TestClient, memory_db_session: AsyncSession
):
    """
    Regression test:
    1. Create/login a user.
    2. Record users.last_login_at.
    3. Call logout.
    4. Reload the user from the database.
    5. Assert that last_login_at is unchanged.
    6. Assert that the refresh token is revoked.
    7. Assert that a LOGOUT audit record exists.
    """
    import hashlib
    from app.models.user import User
    from app.models.audit import AuditLog
    from app.models.user_refresh_token import UserRefreshToken
    from app.utils.security import hash_password

    # 1. Create/login user
    user = User(
        employee_code="EMP-REG-99",
        full_name="Regression User",
        email="regression@example.com",
        password_hash=hash_password("securepassword123"),
        is_active=True,
        is_verified=False,
    )
    memory_db_session.add(user)
    await memory_db_session.commit()

    # Login
    response_login = client.post(
        "/api/v1/auth/login",
        json={"email": "regression@example.com", "password": "securepassword123"},
    )
    assert response_login.status_code == 200
    res_data = response_login.json()
    refresh_token = res_data["refresh_token"]

    # 2. Record users.last_login_at
    await memory_db_session.refresh(user)
    recorded_last_login = user.last_login_at
    assert recorded_last_login is not None

    # 3. Call logout
    response_logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert response_logout.status_code == 200

    # 4. Reload user from database
    await memory_db_session.refresh(user)

    # 5. Assert last_login_at is unchanged
    assert user.last_login_at == recorded_last_login

    # 6. Assert refresh token is revoked
    hashed_token = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    query_token = select(UserRefreshToken).where(UserRefreshToken.token == hashed_token)
    res_token = await memory_db_session.execute(query_token)
    db_token = res_token.scalar_one()
    assert db_token.is_revoked is True

    # 7. Assert LOGOUT audit record exists
    query_logout_audit = select(AuditLog).where(
        AuditLog.action == "LOGOUT",
        AuditLog.user_id == user.id
    )
    res_audit = await memory_db_session.execute(query_logout_audit)
    logout_audit = res_audit.scalar_one_or_none()
    assert logout_audit is not None




