"""
RAG Semantic Retrieval Engine Module.
Retrieves relevant manufacturer document chunks from persistent Chroma vector store with metadata filtering.
"""

from typing import List, Dict, Any, Optional
from backend.rag.ingestion import get_chroma_vector_store, DEFAULT_CHROMA_DIR

def retrieve_pump_context(
    query: str,
    pump_family: Optional[str] = None,
    k: int = 3,
    chroma_dir: str = DEFAULT_CHROMA_DIR
) -> Dict[str, Any]:
    """
    Retrieve relevant manufacturer PDF document chunks matching query and optional pump_family metadata filter.
    Returns concatenated text context and explicit source citations array.
    """
    vector_store = get_chroma_vector_store(chroma_dir)
    
    # Check if vector store has any documents
    coll_data = vector_store.get()
    if not coll_data or not coll_data.get("ids"):
        return {
            "context_text": "No manufacturer PDF datasheets indexed in vector database.",
            "sources": []
        }

    search_kwargs: Dict[str, Any] = {"k": k}
    if pump_family:
        search_kwargs["filter"] = {"pump_family": pump_family.upper()}

    try:
        results = vector_store.similarity_search(query, **search_kwargs)
        # Fallback without filter if filtered search returns empty
        if not results and pump_family:
            results = vector_store.similarity_search(query, k=k)
    except Exception:
        results = vector_store.similarity_search(query, k=k)

    sources = []
    context_chunks = []

    for idx, doc in enumerate(results):
        src_file = doc.metadata.get("source_file", "unknown_document.pdf")
        fam = doc.metadata.get("pump_family", "GENERIC")
        page = doc.metadata.get("page", 1)
        chunk_text = doc.page_content.strip()

        context_chunks.append(f"[Document: {src_file} | Family: {fam} | Page {page}]\n{chunk_text}")
        
        sources.append({
            "document": src_file,
            "pump_family": fam,
            "page": page,
            "chunk_snippet": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
        })

    return {
        "context_text": "\n\n".join(context_chunks) if context_chunks else "No specific manufacturer datasheet chunks found.",
        "sources": sources
    }
