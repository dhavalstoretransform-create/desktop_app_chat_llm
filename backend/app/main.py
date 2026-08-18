"""
ChatLLM — FastAPI application entry point.

Responsibilities:
  - Create the FastAPI instance
  - Register middleware (CORS)
  - Register global exception handlers
  - Mount the root /, /health, and /docs endpoints
  - Mount the versioned /api/v1 router

Keep this file thin.
Business logic lives in services.
"""

from __future__ import annotations

import sys
import os
# Ensure the backend directory is in sys.path for Vercel imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.v1 import api_v1_router
from app.api.v1.health import health_check
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Application instance ─────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Centralized enterprise AI platform.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)


# ── CORS middleware ───────────────────────────────────────────────────────────
# Allow configured origins plus local frontend development servers.

configured_origins = list(settings.BACKEND_CORS_ORIGINS or [])

local_development_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

allowed_origins = list(
    dict.fromkeys(
        configured_origins + local_development_origins
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catch all unhandled exceptions.

    Never expose stack traces, internal messages, or credentials to users.
    Log the full error internally for diagnostics.
    """
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )


# ── Root welcome endpoint ───────────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Root API endpoint")
def root_welcome() -> dict[str, Any]:
    """Return API welcome message and documentation links."""
    return {
        "service": settings.PROJECT_NAME,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


# ── Redirect /docs to versioned docs ─────────────────────────────────────────
@app.get("/docs", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    """Redirect root-level /docs requests to the versioned OpenAPI docs."""
    return RedirectResponse(
        url=f"{settings.API_V1_STR}/docs"
    )


# ── Root /health ─────────────────────────────────────────────────────────────
app.add_api_route(
    "/health",
    health_check,
    methods=["GET"],
    tags=["Health"],
    summary="Root health check",
)

# ── Favicon handler ─────────────────────────────────────────────────────────
@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Return empty 204 No Content for favicon browser requests."""
    return Response(status_code=204)


# ── Versioned API ─────────────────────────────────────────────────────────────
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
