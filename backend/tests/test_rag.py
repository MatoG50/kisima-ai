"""
Automated Test Suite for RAG Pipeline, Ingestion, Chunking, and Retrieval.
"""

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
from backend.rag.metadata import extract_pdf_metadata, map_pump_id_to_family
from backend.rag.chunking import chunk_documents
from backend.rag.retrieval import retrieve_pump_context

def test_extract_pdf_metadata():
    meta1 = extract_pdf_metadata("data/documents/ds5.pdf")
    assert meta1["source_file"] == "ds5.pdf"
    assert meta1["pump_family"] == "DS5"
    assert meta1["document_type"] == "pump_datasheet"

    meta2 = extract_pdf_metadata("data/documents/dsd3.pdf")
    assert meta2["source_file"] == "dsd3.pdf"
    assert meta2["pump_family"] == "DSD3"

def test_map_pump_id_to_family():
    assert map_pump_id_to_family("ds05-17") == "DS5"
    assert map_pump_id_to_family("dsd03-07") == "DSD3"
    assert map_pump_id_to_family("dsp01-05") == "DSP1"
    assert map_pump_id_to_family("dss05-08") == "DSS5"
    assert map_pump_id_to_family("ds14-10") == "DS14"

def test_chunk_documents():
    doc = Document(
        page_content="Dayliff DS submersible boreholes pumps are designed for continuous pumping duty. " * 20,
        metadata={"source_file": "ds5.pdf", "pump_family": "DS5"}
    )
    chunks = chunk_documents([doc], chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.metadata["source_file"] == "ds5.pdf"
        assert chunk.metadata["pump_family"] == "DS5"

def test_retrieve_pump_context():
    res = retrieve_pump_context("submersible borehole pump installation", pump_family="DS5", k=2)
    assert "context_text" in res
    assert "sources" in res
    assert isinstance(res["sources"], list)
