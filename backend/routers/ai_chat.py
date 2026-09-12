import datetime
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from core.rate_limiter import limiter
from core.config import settings
from core.security import get_current_user_optional, UserPlaceholder
from models.database import get_db
from models.aqi_record import AIChatLog
from schemas.chat import ChatRequest, ChatResponse
from services.llm_service import LLMService

router = APIRouter(prefix="/ai", tags=["AI Chat Assistant"])

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.RATE_LIMIT_AI_CHAT_MINUTE}/minute")
@limiter.limit(f"{settings.RATE_LIMIT_AI_CHAT_DAY}/day")
async def chat_with_ai(
    request: Request,
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Submits a health or air-quality question to the AI Assistant.
    Calls backend LLM service (Gemini/OpenAI) or rule-based expert engine,
    without exposing any third-party credentials to the client.
    """
    msg = body.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    city = body.city or "Kanpur"
    current_aqi = body.current_aqi if body.current_aqi is not None else 100.0

    # Generate response
    reply, source = LLMService.generate_health_chat(
        message=msg,
        city=city,
        aqi=current_aqi,
        pollutants=body.pollutants
    )

    # Save turn to database with nullable user_id (for future user account history)
    try:
        chat_log = AIChatLog(
            session_id=request.headers.get("x-session-id"),
            message=msg,
            response=reply,
            city=city,
            current_aqi=current_aqi,
            created_at=datetime.datetime.utcnow(),
            user_id=current_user.id if current_user else None
        )
        db.add(chat_log)
        db.commit()
    except Exception as e:
        print(f"[AIChat] Warning: could not log chat to DB: {e}")

    return ChatResponse(
        reply=reply,
        timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        source=source
    )
