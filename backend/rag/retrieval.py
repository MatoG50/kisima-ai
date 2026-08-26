"""
RAG Semantic Retrieval Engine Module.
Retrieves relevant manufacturer document chunks from persistent Chroma vector store with metadata filtering.
Enforces strict family filtering to prevent cross-family document leakage.
"""

from typing import List, Dict, Any, Optional
from backend.rag.ingestion import get_chroma_vector_store, DEFAULT_CHROMA_DIR
from backend.rag.metadata import extract_family_prefix

ALL_PUMP_FAMILIES = [
    "DS2", "DS3", "DS5", "DS8", "DS14", "DS17", "DS30", "DS46", "DS60", "DS77", "DS95", "DS",
    "DSD2", "DSD3", "DSD5", "DSD8", "DSD",
    "DSP1", "DSP3", "DSP5", "DSP8", "DSP",
    "DSS2", "DSS3", "DSS5", "DSS8", "DSS14", "DSS"
]

def get_families_for_prefix(prefix: str) -> List[str]:
    """
    Get all canonical pump_family metadata strings associated with a family prefix (DSS, DSD, DSP, DS).
    """
    p_upper = prefix.strip().upper()
    return [fam for fam in ALL_PUMP_FAMILIES if extract_family_prefix(fam) == p_upper]

def retrieve_pump_context(
    query: str,
    pump_family: Optional[str] = None,
    family_prefix: Optional[str] = None,
    k: int = 5,
    chroma_dir: str = DEFAULT_CHROMA_DIR
) -> Dict[str, Any]:
    """
    Retrieve relevant manufacturer PDF document chunks matching query and strict family metadata filter.
    Returns concatenated text context and explicit source citations array.
    STRICT: If a family or family_prefix is requested, ONLY documents matching that family/prefix are returned.
    """
    vector_store = get_chroma_vector_store(chroma_dir)
    
    # Check if vector store has any documents
    coll_data = vector_store.get()
    if not coll_data or not coll_data.get("ids"):
        return {
            "context_text": "",
            "sources": [],
            "family_found": False,
            "requested_family": pump_family or family_prefix
        }

    target_prefix = extract_family_prefix(family_prefix or pump_family or "") if (family_prefix or pump_family) else None
    target_family = pump_family.upper() if (pump_family and any(c.isdigit() for c in pump_family)) else None

    # Determine Chroma metadata filter
    search_kwargs: Dict[str, Any] = {"k": k}

    if target_family:
        search_kwargs["filter"] = {"pump_family": target_family}
    elif target_prefix:
        matching_fams = get_families_for_prefix(target_prefix)
        if matching_fams:
            search_kwargs["filter"] = {"pump_family": {"$in": matching_fams}}

    try:
        results = vector_store.similarity_search(query, **search_kwargs)
    except Exception:
        # Fallback query with $in filter if available
        if target_prefix:
            matching_fams = get_families_for_prefix(target_prefix)
            try:
                results = vector_store.similarity_search(query, k=k, filter={"pump_family": {"$in": matching_fams}})
            except Exception:
                results = []
        else:
            try:
                results = vector_store.similarity_search(query, k=k)
            except Exception:
                results = []

    sources = []
    context_chunks = []

    for doc in results:
        src_file = doc.metadata.get("source_file", "unknown_document.pdf")
        fam = doc.metadata.get("pump_family", "GENERIC").upper()
        doc_prefix = extract_family_prefix(fam)
        page = doc.metadata.get("page", 1)
        chunk_text = doc.page_content.strip()

        # STRICT FILTERING: Discard any document chunk that does not match the requested family_prefix
        if target_prefix and doc_prefix != target_prefix:
            continue

        context_chunks.append(f"[Document: {src_file} | Family: {fam} | Page {page}]\n{chunk_text}")
        
        sources.append({
            "document": src_file,
            "pump_family": fam,
            "page": page,
            "chunk_snippet": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
        })

        if len(sources) >= k:
            break

    # STRICT: If target_prefix was requested but 0 matching docs were found after strict filtering
    if target_prefix and not sources:
        return {
            "context_text": "",
            "sources": [],
            "family_found": False,
            "requested_family": target_family or target_prefix
        }

    return {
        "context_text": "\n\n".join(context_chunks) if context_chunks else "",
        "sources": sources,
        "family_found": len(sources) > 0,
        "requested_family": target_family or target_prefix
    }
