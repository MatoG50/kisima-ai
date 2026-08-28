"""
Pytest Configuration & Session Fixtures Module.
Populates test vector store and database prerequisites for reproducible test execution.
"""

import os
import pytest
from backend.rag.ingestion import ingest_pdf_directory, DEFAULT_CHROMA_DIR

@pytest.fixture(scope="session", autouse=True)
def ensure_rag_chroma_populated():
    """
    Ensure the Chroma vector database is populated with manufacturer datasheet embeddings.
    Idempotent: automatically indexes PDF documents if vector store is empty in clean CI environments.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    pdf_dir = os.path.join(base_dir, "data/documents")
    if os.path.exists(pdf_dir):
        ingest_pdf_directory(pdf_dir, DEFAULT_CHROMA_DIR)
