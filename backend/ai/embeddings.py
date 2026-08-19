"""
Embeddings Factory Module.
Provides embedding models for LangChain & Chroma (supporting HuggingFace, OpenAI, and lightweight fallback).
"""

import os
from typing import List, Any
from langchain_core.embeddings import Embeddings

class LightweightHashEmbeddings(Embeddings):
    """
    Deterministic lightweight 384-dimensional embedding generator for local testing & offline environments.
    Guarantees fast, offline, free operation without requiring external API calls or large model downloads.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _embed_text(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        text_lower = text.lower()
        for idx, char in enumerate(text_lower):
            pos = (ord(char) * (idx + 1)) % self.dimension
            vec[pos] += 1.0
        # Normalize vector
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_text(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_text(text)

def get_embedding_model(provider: str = "auto") -> Embeddings:
    """
    Get configured embedding model instance based on environment variables or provider setting.
    """
    env_provider = os.environ.get("EMBEDDINGS_PROVIDER", provider).lower()

    if env_provider == "openai" or (env_provider == "auto" and os.environ.get("OPENAI_API_KEY")):
        try:
            from langchain_community.embeddings import OpenAIEmbeddings
            return OpenAIEmbeddings(model="text-embedding-3-small")
        except Exception:
            pass

    if env_provider in ("huggingface", "sentence-transformers"):
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception:
            pass

    # Default fallback to deterministic lightweight embedding model
    return LightweightHashEmbeddings(dimension=384)
