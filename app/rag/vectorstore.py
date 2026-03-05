from functools import lru_cache
from langchain_postgres import PGVector
from app.core.config import settings
from app.rag.embeddings import get_embedder

@lru_cache
def get_vectorstore() -> PGVector:
    return PGVector(
        embeddings=get_embedder(),
        collection_name="workspace_documents",
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )
