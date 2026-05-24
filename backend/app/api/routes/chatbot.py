from fastapi import APIRouter, Depends, HTTPException
import uuid
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ...auth.deps import get_current_user
from ...db.session import get_db
from ...models import ChatHistory
from ...schemas.chat import ChatHistoryResponse
from ...schemas.chatbot import ChatbotQueryRequest, ChatbotQueryResponse
from ...services.chatbot_service import query_chatbot

router = APIRouter()


@router.post("/chatbot/query", response_model=ChatbotQueryResponse)
async def chatbot_query(
    payload: ChatbotQueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ChatbotQueryResponse:
    try:
        result = await run_in_threadpool(
            query_chatbot,
            payload.query,
            payload.top_k,
            payload.min_score,
            payload.model,
            False,
        )
        answer = result.get("answer", "")
        # Resolve session_id
        session_id = payload.session_id or str(uuid.uuid4())
        
        # Save to history
        chat_history = ChatHistory(
            user_id=current_user.id,
            session_id=session_id,
            query=payload.query,
            answer=answer
        )
        db.add(chat_history)
        db.commit()
        
        result["session_id"] = session_id
        return ChatbotQueryResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chatbot query failed") from exc


@router.get("/chatbot/history", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ChatHistoryResponse]:
    histories = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    return histories

@router.delete("/chatbot/history/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> dict:
    deleted = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.session_id == session_id
    ).delete()
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Session not found or already deleted")
    return {"status": "deleted"}
