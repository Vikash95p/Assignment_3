import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.conversation import Conversation
from app.ai.llm import ai_provider
from app.services.rag_service import rag_service
from app.services.search_service import search_service
from app.services.document_service import document_service
import re

class ChatService:
    def process_chat(self, db: Session, text: str, conversation_id: str, attachments: List[str] = None) -> Message:
        # 1. Fetch history
        history_msgs = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
        history = [{"role": msg.role, "content": msg.content} for msg in history_msgs]
        
        # Determine if we need RAG or Web Search
        # Basic heuristic for MVP:
        # If user asks for "search web" or "latest", trigger search
        # If attachments provided, trigger RAG
        
        context_parts = []
        sources = []
        
        need_web_search = bool(re.search(r'\b(search web|latest|current|today)\b', text.lower()))
        
        image_path = None
        if attachments:
            rag_docs = []
            for att_id in attachments:
                doc = document_service.get_document(db, att_id)
                if doc:
                    if doc.file_type.startswith("image/"):
                        import os
                        from app.core.config import settings
                        image_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
                    else:
                        rag_docs.append(att_id)
            
            if rag_docs:
                rag_results = rag_service.retrieve_relevant_chunks(db, text, top_k=3, document_ids=rag_docs)
                if rag_results:
                    context_parts.append("From your uploaded documents:\n" + "\n---\n".join([r['chunk_text'] for r in rag_results]))
                    sources.extend([{"type": "document", "name": r['document_name'], "id": r['document_id']} for r in rag_results])

        
        if need_web_search:
            web_results = search_service.search_web(text)
            if web_results:
                context_parts.append("From the web:\n" + "\n---\n".join([f"{r['title']} ({r['url']}): {r['snippet']}" for r in web_results]))
                sources.extend([{"type": "web", "title": r['title'], "url": r['url']} for r in web_results])

        context = "\n\n".join(context_parts) if context_parts else None

        # 2. Get AI Response
        ai_response_text = ai_provider.generate_response(prompt=text, context=context, history=history, image_path=image_path)

        # 3. Store User Message
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=text,
            metadata_json={"attachments": attachments} if attachments else {}
        )
        db.add(user_msg)
        
        # 4. Store Assistant Message
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response_text,
            metadata_json={"sources": sources}
        )
        db.add(assistant_msg)
        
        db.commit()
        db.refresh(assistant_msg)
        return assistant_msg

chat_service = ChatService()
