"""
LangChain Document Chunking Module.
Splits extracted PDF text into meaningful chunks while preserving document metadata.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE: int = 600
DEFAULT_CHUNK_OVERLAP: int = 100

def chunk_documents(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[Document]:
    """
    Split a list of LangChain Document objects into smaller text chunks.
    Preserves all original document metadata on each generated chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    return chunks
