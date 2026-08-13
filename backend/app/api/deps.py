"""
Shared API dependencies.

Provides FastAPI dependency injection functions for:
  - Database sessions (get_db, DatabaseDep)
  - Current authenticated user (get_current_user, CurrentUserDep)
"""

from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.security import decode_token

# Typed dependency alias for database session injection in route handlers
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    db: DatabaseDep,
    token: TokenDep,
) -> User:
    """Validate JWT access token and return the active user."""
    import uuid

    from app.repositories.audit_log import AuditLogRepository

    user_id: uuid.UUID | None = None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Invalid token type.")
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Invalid token subject.")
        user_id = uuid.UUID(sub)
    except Exception:
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            sub = unverified.get("sub")
            if sub:
                user_id = uuid.UUID(sub)
        except Exception:
            pass

        user_repo = UserRepository(db)
        exists = False
        if user_id:
            exists = await user_repo.get(user_id) is not None

        audit_repo = AuditLogRepository(db)
        await audit_repo.create(
            obj_in={
                "user_id": user_id if exists else None,
                "action": "AUTHENTICATION_FAILURE",
                "entity_name": "user",
                "entity_id": user_id,
                "description": "Authentication validation failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        ) from None

    user_repo = UserRepository(db)
    user = await user_repo.get_with_permissions(user_id)
    if not user:
        audit_repo = AuditLogRepository(db)
        await audit_repo.create(
            obj_in={
                "user_id": None,
                "action": "AUTHENTICATION_FAILURE",
                "entity_name": "user",
                "entity_id": user_id,
                "description": "Authentication validation failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    if not user.is_active:
        audit_repo = AuditLogRepository(db)
        await audit_repo.create(
            obj_in={
                "user_id": user.id,
                "action": "AUTHENTICATION_FAILURE",
                "entity_name": "user",
                "entity_id": user.id,
                "description": "Authentication validation failed",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user.",
        )
    return user


def require_permission(permission_code: str) -> Callable[..., Any]:
    """Dependency to check if the current user has specific permissions."""
    async def dependency(
        current_user: CurrentUserDep,
        db: DatabaseDep,
    ) -> User:
        if (
            current_user.role
            and current_user.role.is_active
            and current_user.role.permissions
        ):
            for permission in current_user.role.permissions:
                if permission.code == permission_code and permission.is_active:
                    return current_user
        # Write authorization failure to audit log
        from app.repositories.audit_log import AuditLogRepository
        audit_repo = AuditLogRepository(db)
        await audit_repo.create(
            obj_in={
                "user_id": current_user.id,
                "action": "AUTHORIZATION_FAILED",
                "entity_name": "permission",
                "entity_id": current_user.id,
                "description": f"User lacked required permission: {permission_code}",
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return dependency


CurrentUserDep = Annotated[User, Depends(get_current_user)]

__all__ = [
    "DatabaseDep",
    "get_db",
    "CurrentUserDep",
    "get_current_user",
    "require_permission",
]
