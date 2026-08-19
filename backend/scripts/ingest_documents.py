"""
CLI Script for Document Ingestion Pipeline.
Indexes manufacturer PDF datasheets into the local persistent Chroma vector database.
"""

import sys
import os

# Ensure parent root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.rag.ingestion import ingest_pdf_directory, DEFAULT_CHROMA_DIR

def main():
    print("==================================================")
    print("STAGE 6 — RAG PDF DOCUMENT INGESTION PIPELINE")
    print("==================================================")
    
    # Check possible document paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    pdf_dir = os.path.join(base_dir, "data/documents")
    datasheets_dir = os.path.join(base_dir, "data/documents/pump_datasheets")
    
    target_dir = pdf_dir
    if os.path.exists(datasheets_dir) and len(os.listdir(datasheets_dir)) > 0:
        target_dir = datasheets_dir
        
    print(f"Scanning target document directory: {target_dir}")
    print(f"Chroma vector store location:      {DEFAULT_CHROMA_DIR}")
    
    res = ingest_pdf_directory(target_dir, DEFAULT_CHROMA_DIR)
    
    print("\nINGESTION REPORT:")
    print(f"  Status:               {res.get('status')}")
    print(f"  Total PDFs found:     {res.get('total_pdf_files', 0)}")
    print(f"  Files newly indexed:  {res.get('files_newly_indexed', 0)}")
    print(f"  Total chunks stored:  {res.get('chunks_stored', 0)}")
    print("==================================================")
    print("Stage 6 RAG ingestion complete — manufacturer PDFs indexed in persistent Chroma DB.")
    print("==================================================")

if __name__ == '__main__':
    main()
