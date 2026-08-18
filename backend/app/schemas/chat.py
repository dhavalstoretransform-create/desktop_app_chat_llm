from pydantic import BaseModel
import uuid
from datetime import datetime

class ChatCompletionRequest(BaseModel):
    message: str
    model_id: uuid.UUID | None = None
    conversation_id: uuid.UUID | None = None

class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

class ChatModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider: str

class ChatUsageResponse(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    conversation_id: uuid.UUID
    message: ChatMessageResponse
    model: ChatModelResponse
    usage: ChatUsageResponse
    cost: float
