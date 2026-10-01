import os
from typing import List, Optional, Dict, Any
from app.ai.provider import AIProvider
from app.core.config import settings
from google import genai
from google.genai import types

class GeminiProvider(AIProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.LLM_API_KEY)
        self.model = settings.LLM_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL

    def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None, 
        history: Optional[List[Dict[str, Any]]] = None,
        image_path: Optional[str] = None
    ) -> str:
        
        contents = []
        
        if history:
            for msg in history:
                role = 'user' if msg['role'] == 'user' else 'model'
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg['content'])]))

        parts = []
        if context:
            parts.append(types.Part.from_text(text=f"Context information:\n{context}\n\n"))
        
        if image_path and os.path.exists(image_path):
            # We can use the file api or directly upload if supported, but for simplicity
            # we will upload it using files api
            uploaded_file = self.client.files.upload(file=image_path)
            parts.append(types.Part.from_uri(file_uri=uploaded_file.uri, mime_type=uploaded_file.mime_type))

        parts.append(types.Part.from_text(text=prompt))
        
        contents.append(types.Content(role='user', parts=parts))

        # Emotional Support and Persona Instruction
        system_prompt = (
            "You are a helpful, respectful, and empathetic multimodal AI chatbot. "
            "When users express emotional distress, be supportive, non-judgmental, and conversational. "
            "Do NOT claim to be a therapist or doctor, do NOT diagnose, and if the situation is serious, "
            "gently encourage them to seek professional support. Always give clear, well-structured answers "
            "using markdown for technical queries."
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt)
        )
        return response.text

    def generate_embeddings(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text
        )
        return response.embeddings[0].values

    def edit_document(self, content: str, instruction: str) -> str:
        prompt = f"Given the following document content, please apply this instruction: {instruction}\n\nDocument Content:\n{content}\n\nReturn ONLY the modified content, without any extra commentary or markdown codeblocks wrapping the whole thing unless it was there originally."
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text

ai_provider = GeminiProvider()
