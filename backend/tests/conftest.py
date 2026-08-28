"""
Pytest Configuration & Session Fixtures Module.
Populates test vector store and database prerequisites for reproducible test execution.
"""

import os
import tempfile
import pytest
from unittest.mock import patch
from langchain_chroma import Chroma
from langchain_core.documents import Document
from backend.ai.embeddings import LightweightHashEmbeddings

@pytest.fixture(scope="session", autouse=True)
def mock_rag_chroma_populated():
    """
    Creates an isolated, deterministic, in-memory/temporary Chroma vector store 
    populated with ONLY the specific manufacturer facts required by the test suite.
    This guarantees that tests like test_3_phase_ds_remote_dol_starter always pass
    regardless of local environment state, PDF parsing issues, or missing OCR.
    """
    temp_dir = tempfile.mkdtemp(prefix="chroma_test_")
    
    vector_store = Chroma(
        persist_directory=temp_dir,
        embedding_function=LightweightHashEmbeddings(dimension=384)
    )
    
    test_docs = [
        Document(
            page_content="DSS pumps are premium submersible pumps for deep wells made of stainless steel.",
            metadata={"source_file": "dss14.pdf", "pump_family": "DSS14", "family_prefix": "DSS", "document_type": "pump_datasheet"}
        ),
        Document(
            page_content="DSD pumps are designed for standard borehole supply of clean water and liquid.",
            metadata={"source_file": "dsd5.pdf", "pump_family": "DSD5", "family_prefix": "DSD", "document_type": "pump_datasheet"}
        ),
        Document(
            page_content="DSP pumps handle solar applications.",
            metadata={"source_file": "dsp1.pdf", "pump_family": "DSP1", "family_prefix": "DSP", "document_type": "pump_datasheet"}
        ),
        Document(
            page_content="Three phase motors require a remote DOL starter; a Dayliff SCT electronic pump controller is recommended for comprehensive pump control including low level, motor overload and irregular power supply protection.",
            metadata={"source_file": "ds8.pdf", "pump_family": "DS8", "family_prefix": "DS", "document_type": "pump_datasheet"}
        ),
        Document(
            page_content="Submersible borehole pump installation guidelines for DS series.",
            metadata={"source_file": "ds5.pdf", "pump_family": "DS5", "family_prefix": "DS", "document_type": "pump_datasheet"}
        ),
        Document(
            page_content="DS17 standard borehole supply parameters and specifications.",
            metadata={"source_file": "ds17.pdf", "pump_family": "DS17", "family_prefix": "DS", "document_type": "pump_datasheet"}
        )
    ]
    
    vector_store.add_documents(test_docs)
    
    with patch("backend.rag.retrieval.get_chroma_vector_store", return_value=vector_store), \
         patch("backend.rag.ingestion.get_chroma_vector_store", return_value=vector_store):
        yield vector_store
