"""
Authentication schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        description="Email address of the employee",
    )
    password: str = Field(..., description="User's plain text password")
class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class TokenSchema(BaseModel):
    """Schema for returned authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type, defaults to bearer")
    refresh_token: str = Field(..., description="JWT refresh token")
