"""
Authentication API endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, DatabaseDep
from app.repositories.audit_log import AuditLogRepository
from app.repositories.user import UserRepository
from app.repositories.user_refresh_token import UserRefreshTokenRepository
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenSchema
from app.schemas.user import UserRegisterRequest, UserRegisterResponse, UserResponse
from app.services.user import UserService
from app.services.user_refresh_token import UserRefreshTokenService
from app.utils.security import create_access_token, verify_password

router = APIRouter()


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login(
    *,
    db: DatabaseDep,
    login_in: LoginRequest,
) -> Any:
    """Authenticate a user, issue access and refresh tokens, and log the event."""
    user_repo = UserRepository(db)
    audit_repo = AuditLogRepository(db)
    token_repo = UserRefreshTokenRepository(db)
    token_service = UserRefreshTokenService(token_repo)

    user = await user_repo.get_by_email(login_in.email.lower())
    if not user:
        await audit_repo.create(
            obj_in={
                "user_id": None,
                "action": "LOGIN_FAILED",
                "entity_name": "user",
                "entity_id": None,
                "description": "Login attempt failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        await audit_repo.create(
            obj_in={
                "user_id": user.id,
                "action": "LOGIN_FAILED",
                "entity_name": "user",
                "entity_id": user.id,
                "description": "Login attempt failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not verify_password(login_in.password, user.password_hash):
        await audit_repo.create(
            obj_in={
                "user_id": user.id,
                "action": "LOGIN_FAILED",
                "entity_name": "user",
                "entity_id": user.id,
                "description": "Login attempt failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Mark user as verified and update last login time
    from datetime import UTC, datetime
    user_service = UserService(user_repo)
    await user_service.update(
        id=user.id,
        obj_in={
            "is_verified": True,
            "last_login_at": datetime.now(UTC),
        },
    )

    # Issue tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = await token_service.create_token(user_id=user.id)

    # Log successful login
    await audit_repo.create(
        obj_in={
            "user_id": user.id,
            "action": "LOGIN_SUCCESS",
            "entity_name": "user",
            "entity_id": user.id,
            "description": "User logged in successfully",
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def refresh(
    *,
    db: DatabaseDep,
    refresh_in: RefreshTokenRequest,
) -> Any:
    """Validate a refresh token and issue a new access token."""
    token_repo = UserRefreshTokenRepository(db)
    token_service = UserRefreshTokenService(token_repo)
    audit_repo = AuditLogRepository(db)

    user_id = await token_service.verify_and_get_user_id(refresh_in.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    if not user or not user.is_active:
        if user_id:
            await audit_repo.create(
                obj_in={
                    "user_id": user_id,
                    "action": "AUTHENTICATION_FAILURE",
                    "entity_name": "user",
                    "entity_id": user_id,
                    "description": (
                        "Token refresh failed: User account is inactive "
                        "or not found"
                    ),
                }
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found.",
        )

    new_access_token = create_access_token(subject=user.id)

    # Log successful token refresh
    await audit_repo.create(
        obj_in={
            "user_id": user.id,
            "action": "TOKEN_REFRESH",
            "entity_name": "user",
            "entity_id": user.id,
            "description": "User successfully refreshed access token",
        }
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": refresh_in.refresh_token,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    *,
    db: DatabaseDep,
    logout_in: RefreshTokenRequest,
) -> Any:
    """Revoke the refresh token, invalidating the session, and log the event."""
    token_repo = UserRefreshTokenRepository(db)
    token_service = UserRefreshTokenService(token_repo)
    audit_repo = AuditLogRepository(db)

    user_id = await token_service.verify_and_get_user_id(logout_in.refresh_token)
    if user_id:
        await token_service.revoke_token(logout_in.refresh_token)
        # Log successful logout
        await audit_repo.create(
            obj_in={
                "user_id": user_id,
                "action": "LOGOUT",
                "entity_name": "user",
                "entity_id": user_id,
                "description": "User logged out successfully",
            }
        )

    return {"detail": "Successfully logged out."}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(
    current_user: CurrentUserDep,
) -> Any:
    """Get profile information of the currently authenticated user."""
    return current_user


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    *,
    db: DatabaseDep,
    register_in: UserRegisterRequest,
) -> Any:
    """Register a new user identity."""
    from app.repositories.role import RoleRepository
    role_repo = RoleRepository(db)
    employee_role = await role_repo.get_by_code("EMPLOYEE")
    if not employee_role:
        raise HTTPException(status_code=500, detail="EMPLOYEE role not found.")
        
    register_data = register_in.model_dump()
    register_data["role_id"] = employee_role.id
    
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    try:
        user = await user_service.create(obj_in=register_data, current_user=None)
        return user
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            ) from None
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from None

