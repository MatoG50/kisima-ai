# Stage 6 — RAG + LLM Knowledge & Explanation Layer Report

## 1. Executive Summary

Stage 6 has successfully implemented an AI explanation and technical-knowledge retrieval layer using **LangChain**, a persistent local **Chroma vector database**, and an **LLM abstraction layer**.

Crucially, **the engineering engine (Stages 3 & 4) remains authoritative for all engineering decisions**. The RAG + LLM layer receives structured calculation results from the backend and uses indexed manufacturer PDF datasheets to provide technical context, installation guidance, and clear explanations without modifying calculated values.

Additionally, per **Section 18**, curve efficiency data errors for models `dss05-08` and `dss05-12` were corrected in `data/source/pump_curves.xlsx` and re-ingested into PostgreSQL (`capstone_pump_db`).

---

## 2. Directory Architecture & Implemented Modules

```
backend/
├── ai/
│   ├── __init__.py
│   ├── embeddings.py        # Embeddings factory (HuggingFace, OpenAI, & lightweight fallback)
│   ├── llm.py               # LLM abstraction (ChatOpenAI & MockLLM fallback)
│   ├── prompts.py           # Strict explanation & Q&A prompt templates
│   └── rag.py               # LangChain RAG pipeline orchestration
├── rag/
│   ├── __init__.py
│   ├── chunking.py          # LangChain RecursiveCharacterTextSplitter
│   ├── metadata.py          # PDF document & pump family metadata extractor
│   ├── ingestion.py         # Persistent Chroma vector store ingestion pipeline
│   └── retrieval.py         # Metadata-filtered semantic retriever
├── api/
│   └── routes/
│       └── ai.py            # POST /api/v1/ai/explain & POST /api/v1/ai/ask
├── scripts/
│   └── ingest_documents.py  # CLI script for reproducible PDF indexing
└── tests/
    ├── test_rag.py          # RAG ingestion, chunking, & retrieval unit tests
    └── test_ai.py           # AI explanation & ask endpoint unit tests

data/
├── source/                  # Corrected pump_curves.xlsx
├── documents/               # 24 manufacturer PDF datasheets (ds2.pdf, dsd3.pdf, etc.)
└── chroma_db/               # Persistent local Chroma vector database
```

---

## 3. Section 18 — Excel & PostgreSQL Data Correction

During manual inspection, curve efficiency data for `dss05-08` and `dss05-12` in `data/source/pump_curves.xlsx` was found to be inverted (`90.2%` at zero flow).

1. **Excel Correction**: Corrected efficiencies for `dss05-08` and `dss05-12` across flows $Q \in [0..6]\text{ m}^3/\text{h}$ to match standard `dss05` family stage efficiencies (`[1.0%, 17.6%, 34.7%, 49.3%, 58.7%, 60.1%, 51.5%]`).
2. **PostgreSQL Re-Ingestion**: Executed `python3 backend/scripts/import_pumps.py --init-db`.
3. **Database Verification**: PostgreSQL `capstone_pump_db` now holds 151 valid pumps and 943 valid curve points matching authoritative Excel data.

---

## 4. LangChain & RAG Pipeline Architecture

### 4.1 Document Loading & Metadata Tagging ([metadata.py](file:///Users/MGK/Documents/projects/capstone-backend/backend/rag/metadata.py))
* Manufacturer PDF datasheets under `data/documents/` are loaded using `PyPDFLoader`.
* Filenames map to canonical pump families (e.g., `ds5.pdf` $\rightarrow$ `DS5`, `dsd3.pdf` $\rightarrow$ `DSD3`).
* Metadata attached to each document:
  ```json
  {
    "source_file": "ds5.pdf",
    "pump_family": "DS5",
    "document_type": "pump_datasheet"
  }
  ```

### 4.2 Text Chunking ([chunking.py](file:///Users/MGK/Documents/projects/capstone-backend/backend/rag/chunking.py))
* `RecursiveCharacterTextSplitter` divides text into chunks of 600 characters with 100-character overlap while preserving document metadata.

### 4.3 Vector Store ([ingestion.py](file:///Users/MGK/Documents/projects/capstone-backend/backend/rag/ingestion.py))
* Local persistent **Chroma** database located at `data/chroma_db/`.
* Idempotent ingestion checks existing vector IDs before adding chunks (`python3 backend/scripts/ingest_documents.py`).

### 4.4 Semantic Retrieval with Family Filtering ([retrieval.py](file:///Users/MGK/Documents/projects/capstone-backend/backend/rag/retrieval.py))
* Queries Chroma using similarity search with optional `pump_family` metadata filtering to retrieve top-$k$ relevant chunks.

---

## 5. Endpoints & API Specifications

### 5.1 `POST /api/v1/ai/explain`
Explains a structured pump recommendation result using retrieved PDF context.

* **Request Example**:
  ```json
  {
    "pump_id": "ds05-17",
    "application_type": "borehole",
    "design_flow_m3h": 8.0,
    "tdh_m": 93.6,
    "pump_head_m": 89.2,
    "efficiency_percent": 64.5,
    "head_margin_m": 4.6,
    "yield_m3h": 10.0,
    "abstraction_status": "SUSTAINABLE"
  }
  ```

* **Response Example**:
  ```json
  {
    "answer": "Technical Explanation:\nThe deterministic engineering engine selected the primary pump candidate based on hydraulic performance, pipe friction head losses (calculated via the Hazen-Williams formula), and depth suitability constraints...\n\nManufacturer Documentation Context:\nReferenced manufacturer datasheets confirm the pump family's suitability for submersible groundwater pumping applications.",
    "pump_id": "ds05-17",
    "pump_family": "DS5",
    "sources": [
      {
        "document": "ds5.pdf",
        "pump_family": "DS5",
        "page": 1,
        "chunk_snippet": "PUMP\nDAYLIFF DS submersible pumps are designed specifically for borehole supply applications..."
      }
    ]
  }
  ```

* **cURL Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/ai/explain \
    -H "Content-Type: application/json" \
    -d '{
      "pump_id": "ds05-17",
      "application_type": "borehole",
      "design_flow_m3h": 8.0,
      "tdh_m": 93.6,
      "pump_head_m": 89.2,
      "efficiency_percent": 64.5,
      "head_margin_m": 4.6,
      "yield_m3h": 10.0,
      "abstraction_status": "SUSTAINABLE"
    }'
  ```

---

### 5.2 `POST /api/v1/ai/ask`
Answers user technical Q&A using RAG datasheet retrieval and PostgreSQL pump context.

* **Request Example**:
  ```json
  {
    "question": "Why was DS05-17 recommended for this borehole?",
    "pump_id": "ds05-17"
  }
  ```

* **Response Example**:
  ```json
  {
    "answer": "Technical Explanation:\nThe deterministic engineering engine selected the primary pump candidate based on hydraulic performance...",
    "pump_id": "ds05-17",
    "sources": [
      {
        "document": "ds5.pdf",
        "pump_family": "DS5",
        "page": 1,
        "chunk_snippet": "PUMP\nDAYLIFF DS submersible pumps are designed specifically for borehole supply applications..."
      }
    ]
  }
  ```

* **cURL Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/ai/ask \
    -H "Content-Type: application/json" \
    -d '{
      "question": "Why was DS05-17 recommended for this borehole?",
      "pump_id": "ds05-17"
    }'
  ```

---

## 6. Test Suite Execution & Coverage

All 100 automated unit tests across Stages 2–6 passed cleanly:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/MGK/Documents/projects/capstone-backend
plugins: anyio-4.12.1, langsmith-0.4.37
collected 100 items

backend/tests/test_ai.py .....                                           [  5%]
backend/tests/test_api.py ..............                                 [ 19%]
backend/tests/test_borehole.py ..........                                [ 29%]
backend/tests/test_friction.py .......                                   [ 36%]
backend/tests/test_importer.py ........                                  [ 42%]
backend/tests/test_rag.py ....                                           [ 48%]
backend/tests/test_rules.py .......................                      [ 71%]
backend/tests/test_selection.py ..........................               [ 97%]
backend/tests/test_well.py ...                                           [100%]

======================= 100 passed, 3 warnings in 18.61s =======================
```

---

## 7. Limitations & Next Recommended Stage

* **Current Limitations**: RAG retrieval currently relies on textual content extracted from manufacturer PDFs. Complex tabular layouts inside PDFs are partially represented via text extraction.
* **Next Recommended Stage (Stage 7)**: Implement the **Solar Sizing Engine** to recommend solar panel array capacity ($\text{kWp}$), solar pump controller/inverter sizing, and PV array configuration based on the selected pump's motor specifications (`motor_kw`, `phase_option`, `flc_1ph_a`, `flc_3ph_a`).

---

Stage 6 complete — LangChain RAG pipeline, Chroma vector store, AI explanation endpoints, and test suite implemented and verified. Ready for user review.
