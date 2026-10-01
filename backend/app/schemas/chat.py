from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    attachments: Optional[List[str]] = [] # IDs of uploaded documents

class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = []
    metadata: Optional[Dict[str, Any]] = {}
