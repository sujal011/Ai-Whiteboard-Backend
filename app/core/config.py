from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Whiteboard API"
    
    # Database
    DATABASE_URL: str = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB_NAME')}"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "1")) # 1 days
    
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # ── Embeddings ────────────────────────────────────────────────────────
    embedding_model: str = os.getenv("EMBEDDING_MODEL")

    embedding_model_device: str = os.getenv("EMBEDDING_MODEL_DEVICE")
    embedding_model_normalize: bool = os.getenv("NORMALIZE_EMBEDDINGS")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the env file

settings = Settings()
