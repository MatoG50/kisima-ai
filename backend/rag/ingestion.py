"""
Chroma Vector Store Ingestion Pipeline Module.
Extracts, cleans, chunks, and indexes manufacturer PDF datasheets into a local persistent Chroma database.
"""

import os
import glob
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma

from backend.rag.metadata import extract_pdf_metadata
from backend.rag.chunking import chunk_documents
from backend.ai.embeddings import get_embedding_model

DEFAULT_CHROMA_DIR = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")

def get_chroma_vector_store(chroma_dir: str = DEFAULT_CHROMA_DIR) -> Chroma:
    """
    Get or initialize local persistent Chroma vector store instance.
    """
    embedding_model = get_embedding_model()
    abs_chroma_dir = os.path.abspath(chroma_dir)
    os.makedirs(abs_chroma_dir, exist_ok=True)
    
    vector_store = Chroma(
        persist_directory=abs_chroma_dir,
        embedding_function=embedding_model,
        collection_name="pump_datasheets"
    )
    return vector_store

def ingest_pdf_directory(pdf_dir: str, chroma_dir: str = DEFAULT_CHROMA_DIR) -> Dict[str, Any]:
    """
    Ingest all PDF files from a directory into local persistent Chroma vector store.
    Idempotent: prevents duplicate vector creation by checking existing document sources.
    """
    abs_pdf_dir = os.path.abspath(pdf_dir)
    if not os.path.exists(abs_pdf_dir):
        return {
            "status": "ERROR",
            "message": f"PDF directory '{pdf_dir}' does not exist.",
            "documents_indexed": 0,
            "chunks_stored": 0
        }

    pdf_files = glob.glob(os.path.join(abs_pdf_dir, "*.pdf"))
    if not pdf_files:
        return {
            "status": "WARNING",
            "message": f"No PDF files found in '{pdf_dir}'.",
            "documents_indexed": 0,
            "chunks_stored": 0
        }

    vector_store = get_chroma_vector_store(chroma_dir)
    
    # Check existing source files in collection
    existing_collection = vector_store.get()
    existing_sources = set()
    if existing_collection and "metadatas" in existing_collection and existing_collection["metadatas"]:
        for meta in existing_collection["metadatas"]:
            if meta and "source_file" in meta:
                existing_sources.add(meta["source_file"])

    total_chunks_added = 0
    files_indexed = 0

    for pdf_path in pdf_files:
        meta_dict = extract_pdf_metadata(pdf_path)
        source_file = meta_dict["source_file"]

        # Skip if already ingested idempotently
        if source_file in existing_sources:
            continue

        try:
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()
            
            # Attach custom metadata to each loaded document page
            for doc in raw_docs:
                doc.metadata.update(meta_dict)
                doc.metadata["page"] = doc.metadata.get("page", 0) + 1

            chunks = chunk_documents(raw_docs)
            if chunks:
                ids = [f"{source_file}_p{c.metadata.get('page', 1)}_c{idx}" for idx, c in enumerate(chunks)]
                vector_store.add_documents(chunks, ids=ids)
                total_chunks_added += len(chunks)
                files_indexed += 1
        except Exception as e:
            print(f"Warning: Failed to load PDF '{source_file}': {e}")

    return {
        "status": "SUCCESS",
        "total_pdf_files": len(pdf_files),
        "files_newly_indexed": files_indexed,
        "chunks_stored": total_chunks_added,
        "chroma_dir": os.path.abspath(chroma_dir)
    }
