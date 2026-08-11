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

# .env lives at the repository root (two levels above backend/app/core/)
_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    PROJECT_NAME: str = "ChatLLM"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+psycopg://user:password@localhost:5432/chatllm_db"
    )

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
