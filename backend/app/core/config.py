"""
Application configuration.

All settings are loaded from environment variables or a .env file.
Never hardcode secrets. Never import from this module inside type annotations
that run at module load time if they create circular imports.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    PROJECT_NAME: str = "ChatLLM"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://user:password@localhost:5432/chatllm_db"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        """
        Validate and normalize DATABASE_URL to consistently use asyncpg.
        """
        if not v:
            raise ValueError("DATABASE_URL must be configured")
        
        # Normalize postgresql schemes to asyncpg
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql+psycopg://"):
            v = v.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

        # Translate query parameters for asyncpg compatibility
        if "sslmode=" in v:
            import re
            v = re.sub(r"sslmode=[^&]+", "ssl=require", v)
        if "channel_binding=" in v:
            import re
            v = re.sub(r"channel_binding=[^&]+&?", "", v)
            v = v.rstrip("&?")

        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                f"Invalid DATABASE_URL scheme. Expected postgresql+asyncpg://, got: {v}"
            )
        return v

    # ── Security / JWT ────────────────────────────────────────────────────────
    # Used from Phase 3 onwards.
    JWT_SECRET: str = "changeme_replace_before_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # ── AI Provider Keys (Phase 9+) ───────────────────────────────────────────
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None

    # ── CORS ─────────────────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors(cls, v: object) -> object:
        """Accept BACKEND_CORS_ORIGINS as a JSON string in .env."""
        if isinstance(v, str):
            return json.loads(v)
        return v


settings = Settings()
