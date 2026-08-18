"""
Conversations API router.
"""

from __future__ import annotations

from fastapi import APIRouter, Query, Depends

from app.api.deps import CurrentUserDep, DatabaseDep
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationListResponse,
    ConversationMessagesListResponse
)
from app.services.conversation import ConversationService

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    db: DatabaseDep,
    current_user: CurrentUserDep,
):
    """
    Create a new chat conversation for the authenticated user.
    """
    return await ConversationService.create_conversation(db, current_user, data)

@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List conversations belonging to the authenticated user.
    """
    return await ConversationService.get_conversations(db, current_user, page, page_size)

import uuid

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: DatabaseDep,
    current_user: CurrentUserDep,
):
    """
    Get a single conversation by ID.
    """
    return await ConversationService.get_conversation(db, current_user, conversation_id)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: DatabaseDep,
    current_user: CurrentUserDep,
):
    """
    Delete a conversation and all its associated messages.
    """
    return await ConversationService.delete_conversation(db, current_user, conversation_id)

@router.get("/{conversation_id}/messages", response_model=ConversationMessagesListResponse)
async def get_conversation_messages(
    conversation_id: uuid.UUID,
    db: DatabaseDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get messages for a specific conversation in chronological order.
    """
    return await ConversationService.get_conversation_messages(db, current_user, conversation_id, page, page_size)
