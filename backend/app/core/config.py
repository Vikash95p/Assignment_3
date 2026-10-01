import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+pg8000://postgres:postgres@localhost:5432/multimodal_ai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-3.1-pro"
    EMBEDDING_MODEL: str = "text-embedding-004"
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
