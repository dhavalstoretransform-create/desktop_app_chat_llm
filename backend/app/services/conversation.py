import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User
from app.models.ai_model import AIModel
from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.models.usage import TokenUsage
from app.models.prompt_log import PromptLog
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationListResponse,
    ConversationResponse,
    ConversationMessagesListResponse,
    ConversationMessageResponse
)

class ConversationService:
    @staticmethod
    async def create_conversation(db: AsyncSession, current_user: User, data: ConversationCreate) -> ChatSession:
        from app.repositories.ai_model import AIModelRepository
        # Validate Model
        model = await AIModelRepository(db).get(data.model_id)
        if not model:
            raise HTTPException(status_code=404, detail="AI Model not found")
            
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=current_user.id,
            model_id=model.id,
            session_title=data.title,
            started_at=datetime.now(timezone.utc)
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_conversations(
        db: AsyncSession, 
        current_user: User, 
        page: int = 1, 
        page_size: int = 20
    ) -> ConversationListResponse:
        
        query = select(ChatSession)
        count_query = select(func.count(ChatSession.id))
        
        # User only gets their own conversations
        query = query.where(ChatSession.user_id == current_user.id)
        count_query = count_query.where(ChatSession.user_id == current_user.id)
            
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(desc(ChatSession.started_at)).offset((page - 1) * page_size).limit(page_size)
        items = (await db.execute(query)).scalars().all()
        
        return ConversationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    @staticmethod
    async def get_conversation(db: AsyncSession, current_user: User, conversation_id: uuid.UUID) -> ChatSession:
        stmt = select(ChatSession).where(ChatSession.id == conversation_id, ChatSession.user_id == current_user.id)
        session = (await db.execute(stmt)).scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return session

    @staticmethod
    async def delete_conversation(db: AsyncSession, current_user: User, conversation_id: uuid.UUID) -> dict:
        session = await ConversationService.get_conversation(db, current_user, conversation_id)
        
        # Delete related records
        await db.execute(delete(TokenUsage).where(TokenUsage.session_id == conversation_id))
        await db.execute(delete(PromptLog).where(PromptLog.session_id == conversation_id))
        await db.execute(delete(ChatMessage).where(ChatMessage.session_id == conversation_id))
        await db.execute(delete(ChatSession).where(ChatSession.id == conversation_id))
        
        await db.commit()
        return {"status": "success", "message": "Conversation deleted successfully"}

    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession, 
        current_user: User, 
        conversation_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50
    ) -> ConversationMessagesListResponse:
        # Verify ownership
        await ConversationService.get_conversation(db, current_user, conversation_id)
        
        query = select(ChatMessage).where(ChatMessage.session_id == conversation_id)
        count_query = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == conversation_id)
        
        total = (await db.execute(count_query)).scalar() or 0
        
        # Sort chronologically
        query = query.order_by(asc(ChatMessage.created_at)).offset((page - 1) * page_size).limit(page_size)
        db_messages = (await db.execute(query)).scalars().all()
        
        messages = [
            ConversationMessageResponse(
                id=msg.id,
                role=msg.sender_type,
                content=msg.message_content,
                created_at=msg.created_at
            ) for msg in db_messages
        ]
        
        return ConversationMessagesListResponse(
            conversation_id=conversation_id,
            messages=messages,
            total=total,
            page=page,
            page_size=page_size
        )
