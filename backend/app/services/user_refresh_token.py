"""
UserRefreshToken service encapsulating business rules for user refresh tokens.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.models.user_refresh_token import UserRefreshToken
from app.repositories.user_refresh_token import UserRefreshTokenRepository
from app.services.base import BaseService
from app.utils.security import create_refresh_token, decode_token


class UserRefreshTokenService(
    BaseService[UserRefreshToken, UserRefreshTokenRepository]
):
    """Service class handling user refresh token operations."""

    def __init__(self, repository: UserRefreshTokenRepository) -> None:
        super().__init__(repository=repository)

    async def create_token(self, user_id: uuid.UUID) -> str:
        """Create a new JWT refresh token and store it in the database."""
        token_str = create_refresh_token(subject=user_id)
        
        # Decode to get exp time
        payload = decode_token(token_str)
        exp_timestamp = payload["exp"]
        expires_at = datetime.fromtimestamp(exp_timestamp, tz=UTC)

        # Hash the token string before saving
        import hashlib
        hashed_token = hashlib.sha256(token_str.encode("utf-8")).hexdigest()

        await self.create(
            obj_in={
                "user_id": user_id,
                "token": hashed_token,
                "expires_at": expires_at,
                "is_revoked": False,
            }
        )
        return token_str

    async def verify_and_get_user_id(self, token: str) -> uuid.UUID | None:
        """Verify refresh token in DB, check expiry/revocation, return user_id."""
        db_token = await self.repository.get_by_token(token)
        if not db_token or db_token.is_revoked:
            return None

        expires_at = db_token.expires_at
        if expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)

        now = datetime.now(UTC).replace(tzinfo=None)

        if expires_at <= now:
            return None

        try:
            payload = decode_token(token)
            if payload.get("type") != "refresh":
                return None
            return uuid.UUID(payload["sub"])
        except Exception:
            return None

    async def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token by setting is_revoked to True."""
        db_token = await self.repository.get_by_token(token)
        if not db_token:
            return False
        await self.update(id=db_token.id, obj_in={"is_revoked": True})
        return True
