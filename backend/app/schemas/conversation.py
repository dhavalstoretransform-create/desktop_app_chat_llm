from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class ConversationCreate(BaseModel):
    title: str
    model_id: uuid.UUID

class ConversationResponse(BaseModel):
    id: uuid.UUID
    session_title: str | None = None
    model_id: uuid.UUID
    user_id: uuid.UUID
    session_status: str
    total_messages: int
    started_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int

class ConversationMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationMessagesListResponse(BaseModel):
    conversation_id: uuid.UUID
    messages: list[ConversationMessageResponse]
    total: int
    page: int
    page_size: int
