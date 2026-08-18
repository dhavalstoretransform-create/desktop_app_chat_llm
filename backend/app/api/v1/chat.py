"""
Chat API router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserDep, DatabaseDep
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat import ChatService

router = APIRouter()

@router.post("/completions", response_model=ChatCompletionResponse, status_code=201)
async def process_chat_completion(
    request: ChatCompletionRequest,
    db: DatabaseDep,
    current_user: CurrentUserDep,
):
    """
    Process an AI chat completion, loading conversation history if provided, and persisting usage analytics.
    """
    return await ChatService.process_completion(db, current_user, request)
