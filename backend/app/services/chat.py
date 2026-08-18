import uuid
from datetime import datetime, timezone
import hashlib
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.user import User
from app.models.ai_model import AIModel
from app.models.session import ChatSession
from app.models.message import ChatMessage
from app.models.prompt_log import PromptLog
from app.models.usage import TokenUsage
from app.models.setting import SystemSetting
from app.models.wallet import EmployeeTokenWallet
from app.models.token_transaction import TokenTransaction
from app.models.audit import AuditLog

from app.schemas.chat import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    ChatMessageResponse, 
    ChatModelResponse, 
    ChatUsageResponse
)
from app.services.ai_gateway import AIGateway

class ChatService:
    @staticmethod
    async def process_completion(db: AsyncSession, current_user: User, request: ChatCompletionRequest) -> ChatCompletionResponse:
        
        # 1. Determine Model ID
        model_id = request.model_id
        if not model_id:
            stmt = select(SystemSetting).where(SystemSetting.setting_key == "default_model_id")
            setting = (await db.execute(stmt)).scalar_one_or_none()
            if not setting or not setting.setting_value:
                raise HTTPException(status_code=400, detail="No model provided and no default model configured.")
            try:
                model_id = uuid.UUID(setting.setting_value)
            except ValueError:
                raise HTTPException(status_code=500, detail="Invalid default model configuration.")

        # 2. Validate Model & Provider
        stmt = select(AIModel).options(selectinload(AIModel.provider)).where(AIModel.id == model_id)
        model = (await db.execute(stmt)).scalar_one_or_none()
        
        if not model:
            raise HTTPException(status_code=404, detail="AI Model not found")
        if not model.is_active:
            raise HTTPException(status_code=400, detail="AI Model is not active")
        if not model.provider:
            raise HTTPException(status_code=400, detail="AI Provider not found")
        if not model.provider.is_active:
            raise HTTPException(status_code=400, detail="AI Provider is not active")
            
        # 3. Check Wallet Pre-condition
        wallet_stmt = select(EmployeeTokenWallet).where(EmployeeTokenWallet.user_id == current_user.id)
        wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
        
        if not wallet or wallet.available_tokens <= 0:
            raise HTTPException(
                status_code=402, 
                detail={
                    "code": "INSUFFICIENT_TOKENS",
                    "message": "Insufficient token balance."
                }
            )
            
        # 4. Get or Create Session
        history_text = ""
        if request.conversation_id:
            stmt = select(ChatSession).where(ChatSession.id == request.conversation_id)
            session = (await db.execute(stmt)).scalar_one_or_none()
            if not session or session.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Conversation not found")
                
            # Load History (Limit to last 5 messages for context window)
            history_stmt = select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(asc(ChatMessage.created_at))
            history_msgs = (await db.execute(history_stmt)).scalars().all()
            for msg in history_msgs[-5:]:
                history_text += f"{msg.sender_type}: {msg.message_content}\n"
        else:
            session = ChatSession(
                id=uuid.uuid4(),
                user_id=current_user.id,
                model_id=model.id,
                session_title=request.message.split("\n")[0].strip()[:50].title() if request.message else "New Conversation",
                started_at=datetime.now(timezone.utc)
            )
            db.add(session)
            
        # 5. Create User Message
        user_message = ChatMessage(
            id=uuid.uuid4(),
            session_id=session.id,
            sender_type="user",
            message_type="text",
            message_content=request.message,
            message_order=1 # Simplification
        )
        db.add(user_message)
        await db.flush() # Ensure session has an ID if it was just created
        
        # 6. Call Real AI Provider Gateway
        try:
            gateway_result = await AIGateway.complete(
                model=model,
                prompt=request.message,
                history=history_text
            )
        except Exception as e:
            # Audit log on failure
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=current_user.id,
                action="CHAT_COMPLETION",
                entity_name="ChatSession",
                entity_id=session.id,
                description=f"FAILED: {str(e)}"
            )
            db.add(audit_log)
            await db.commit()
            raise HTTPException(status_code=502, detail=f"AI Provider error: {str(e)}")
            
        ai_response_text = gateway_result.get("content", "")
        input_tokens = gateway_result.get("input_tokens", 0)
        output_tokens = gateway_result.get("output_tokens", 0)
        total_tokens = gateway_result.get("total_tokens", 0)
        response_time_ms = gateway_result.get("response_time_ms", 0)
        
        # Ensure sufficient wallet balance post-call (to prevent negative balance)
        if wallet.available_tokens < total_tokens:
            total_tokens = wallet.available_tokens # Cap deduction
            # In a real app we might still fail or warn here
            
        wallet.available_tokens -= total_tokens
        wallet.total_tokens_used_today += total_tokens
        db.add(wallet)
        
        # Calculate Costs
        input_cost = (Decimal(str(input_tokens)) * (model.input_token_price or Decimal("0"))) / Decimal("1000000")
        output_cost = (Decimal(str(output_tokens)) * (model.output_token_price or Decimal("0"))) / Decimal("1000000")
        total_cost = input_cost + output_cost
        
        # 7. Create AI Message
        ai_message = ChatMessage(
            id=uuid.uuid4(),
            session_id=session.id,
            sender_type="assistant",
            message_type="text",
            message_content=ai_response_text,
            message_order=2,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time_ms
        )
        db.add(ai_message)
        
        # 8. Persist Prompt Log
        prompt_hash = hashlib.sha256(request.message.encode()).hexdigest()
        prompt_log = PromptLog(
            id=uuid.uuid4(),
            user_id=current_user.id,
            session_id=session.id,
            message_id=ai_message.id,
            model_id=model.id,
            prompt_text=request.message,
            response_text=ai_response_text,
            prompt_hash=prompt_hash,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            response_time_ms=response_time_ms,
            status="completed"
        )
        db.add(prompt_log)
        
        # 9. Persist Token Usage
        token_usage = TokenUsage(
            id=uuid.uuid4(),
            user_id=current_user.id,
            session_id=session.id,
            prompt_log_id=prompt_log.id,
            model_id=model.id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            usage_date=datetime.now(timezone.utc).date()
        )
        db.add(token_usage)
        
        # 10. Persist Token Transaction
        token_transaction = TokenTransaction(
            id=uuid.uuid4(),
            user_id=current_user.id,
            conversation_id=session.id,
            model_id=model.id,
            transaction_type="CHAT_COMPLETION",
            transaction_action="DEBIT",
            tokens=total_tokens,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(token_transaction)
        
        # 11. Persist Audit Log
        audit_log = AuditLog(
            id=uuid.uuid4(),
            user_id=current_user.id,
            action="CHAT_COMPLETION",
            entity_name="ChatSession",
            entity_id=session.id,
            description="SUCCESS"
        )
        db.add(audit_log)
        
        await db.commit()
        await db.refresh(ai_message) # To get the created_at timestamp
        
        # Extend the response dictionary explicitly without breaking schema
        response_data = {
            "conversation_id": str(session.id),
            "message": {
                "id": str(ai_message.id),
                "role": ai_message.sender_type,
                "content": ai_message.message_content,
                "created_at": ai_message.created_at or datetime.now(timezone.utc)
            },
            "model": {
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider.name if model.provider else "Unknown"
            },
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            },
            "cost": float(total_cost),
            "wallet": {
                "remaining_tokens": wallet.available_tokens
            }
        }
        
        # We can just return it, FastAPI will serialize properly based on schema, ignoring extra fields unless extra='allow'
        return response_data
