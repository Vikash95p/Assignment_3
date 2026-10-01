from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.models.conversation import Conversation

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.conversation_id:
        conversation = Conversation()
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        request.conversation_id = conversation.id
        
    try:
        assistant_msg = chat_service.process_chat(db, request.message, request.conversation_id, request.attachments)
        
        return ChatResponse(
            id=assistant_msg.id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            conversation_id=assistant_msg.conversation_id,
            sources=assistant_msg.metadata_json.get("sources", []),
            metadata=assistant_msg.metadata_json
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
