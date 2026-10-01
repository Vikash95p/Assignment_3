from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class AIProvider(ABC):
    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None, 
        history: Optional[List[Dict[str, Any]]] = None,
        image_path: Optional[str] = None
    ) -> str:
        pass
    
    @abstractmethod
    def generate_embeddings(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def edit_document(self, content: str, instruction: str) -> str:
        pass
