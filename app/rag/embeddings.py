"""
Embedding utility — singleton OpenAI embedder shared across the app.
Used by: rag_retriever tool, knowledge ingestor (Celery task in Phase 5).
"""

from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings

model_name = settings.embedding_model
model_kwargs = {"device": settings.embedding_model_device}
encode_kwargs = {"normalize_embeddings": settings.embedding_model_normalize}

@lru_cache
def get_embedder() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )