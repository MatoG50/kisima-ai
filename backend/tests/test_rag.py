"""
Automated Test Suite for RAG Pipeline, Ingestion, Chunking, Strict Family Filtering, and Retrieval.
"""

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
from backend.rag.metadata import (
    extract_pdf_metadata,
    map_pump_id_to_family,
    extract_family_prefix,
    detect_pump_family_from_query
)
from backend.rag.chunking import chunk_documents
from backend.rag.retrieval import retrieve_pump_context
from backend.ai.rag import ask_question

def test_extract_pdf_metadata():
    meta1 = extract_pdf_metadata("data/documents/ds5.pdf")
    assert meta1["source_file"] == "ds5.pdf"
    assert meta1["pump_family"] == "DS5"
    assert meta1["family_prefix"] == "DS"
    assert meta1["document_type"] == "pump_datasheet"

    meta2 = extract_pdf_metadata("data/documents/dsd3.pdf")
    assert meta2["source_file"] == "dsd3.pdf"
    assert meta2["pump_family"] == "DSD3"
    assert meta2["family_prefix"] == "DSD"

    meta3 = extract_pdf_metadata("data/documents/dss14.pdf")
    assert meta3["source_file"] == "dss14.pdf"
    assert meta3["pump_family"] == "DSS14"
    assert meta3["family_prefix"] == "DSS"

def test_map_pump_id_to_family():
    assert map_pump_id_to_family("ds05-17") == "DS5"
    assert map_pump_id_to_family("dsd03-07") == "DSD3"
    assert map_pump_id_to_family("dsp01-05") == "DSP1"
    assert map_pump_id_to_family("dss05-08") == "DSS5"
    assert map_pump_id_to_family("ds14-10") == "DS14"

def test_detect_pump_family_from_query():
    # Prefix-only queries
    fam, prefix = detect_pump_family_from_query("What materials are used in DSS pump?")
    assert prefix == "DSS"

    fam, prefix = detect_pump_family_from_query("What electrical options exist for DSD series?")
    assert prefix == "DSD"

    fam, prefix = detect_pump_family_from_query("What solar voltage is used for DSP?")
    assert prefix == "DSP"

    fam, prefix = detect_pump_family_from_query("What is the maximum depth for DS pump?")
    assert prefix == "DS"

    # Specific model queries
    fam, prefix = detect_pump_family_from_query("What is the maximum depth for DSD3?")
    assert fam == "DSD3"
    assert prefix == "DSD"

    fam, prefix = detect_pump_family_from_query("What materials are in DSS14?")
    assert fam == "DSS14"
    assert prefix == "DSS"

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

def test_retrieve_pump_context_strict_family():
    res = retrieve_pump_context("submersible borehole pump installation", pump_family="DS5", k=2)
    assert "context_text" in res
    assert "sources" in res
    assert isinstance(res["sources"], list)
    for src in res["sources"]:
        assert extract_family_prefix(src["pump_family"]) == "DS"

def test_strict_dss_family_retrieval():
    res = ask_question("What materials are used in DSS pump?")
    assert "sources" in res
    assert len(res["sources"]) > 0
    # Every returned source must belong strictly to the DSS family
    for src in res["sources"]:
        assert extract_family_prefix(src["pump_family"]) == "DSS"
        assert src["document"].startswith("dss")
    assert "DSS" in res["answer"] or "stainless steel" in res["answer"].lower()

def test_strict_dsd_family_retrieval():
    res = ask_question("What materials are used in DSD pump?")
    assert "sources" in res
    assert len(res["sources"]) > 0
    for src in res["sources"]:
        assert extract_family_prefix(src["pump_family"]) == "DSD"
        assert src["document"].startswith("dsd")

def test_strict_dsp_family_retrieval():
    res = ask_question("What solar options exist for DSP pump?")
    assert "sources" in res
    assert len(res["sources"]) > 0
    for src in res["sources"]:
        assert extract_family_prefix(src["pump_family"]) == "DSP"
        assert src["document"].startswith("dsp")

def test_strict_ds_family_retrieval():
    res = ask_question("What materials are used in DS pump?")
    assert "sources" in res
    assert len(res["sources"]) > 0
    for src in res["sources"]:
        assert extract_family_prefix(src["pump_family"]) == "DS"
        assert src["document"].startswith("ds")

def test_unsupported_family_query_returns_insufficient_context():
    res = ask_question("What materials are used in XYZ999 pump?")
    assert res["sources"] == []
    assert "No relevant manufacturer datasheet documentation found" in res["answer"]
    assert "XYZ999" in res["answer"]

def test_direct_answer_no_meta_response():
    res = ask_question("What type of liquid can DSD5 pump handle?")
    assert "sources" in res
    assert len(res["sources"]) > 0
    answer_lower = res["answer"].lower()
    
    # Assert that the answer doesn't contain generic meta-phrases
    meta_phrases = [
        "detailed in the datasheet",
        "according to the documentation",
        "please refer to",
        "the available manufacturer documentation provides"
    ]
    for phrase in meta_phrases:
        assert phrase not in answer_lower, f"Answer contains prohibited meta-phrase: '{phrase}'"
        
    # Assert that it actually contains factual keywords likely found in the context (e.g. clean water, liquid, etc)
    assert "water" in answer_lower or "liquid" in answer_lower or "clean" in answer_lower

def test_unsupported_question_with_valid_context_returns_insufficient_context():
    # DS17 is a valid family and ds17.pdf will be retrieved
    res = ask_question("Does DS17 feature integrated Bluetooth control?")
    
    # Assert that documents WERE actually retrieved
    assert "sources" in res
    assert len(res["sources"]) > 0
    
    # But because the documents don't contain info about Bluetooth control,
    # it must return the exact insufficient-context response
    expected_response = "The available manufacturer documentation does not provide enough information to answer that question."
    assert res["answer"].strip() == expected_response


def test_3_phase_ds_remote_dol_starter():
    res = ask_question("Do 3-phase DS pumps require a remote DOL starter?")
    
    # Assert documents were retrieved
    assert "sources" in res
    assert len(res["sources"]) > 0
    
    answer = res["answer"].lower()
    # Ensure it's not the insufficient context response
    assert "does not provide enough information" not in answer
    
    # Ensure it extracted the remote DOL starter info
    assert "remote dol starter" in answer or "remote starter" in answer
    assert "three phase" in answer or "3-phase" in answer


