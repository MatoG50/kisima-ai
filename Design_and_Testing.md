# Kisima AI — System Design and Testing Documentation

This document details the architectural design, engineering patterns, automated testing suite, and deployment cost analysis for **Kisima AI**, an AI-assisted water pump sizing and recommendation application developed for the Quantic MSSE Capstone project.

---

# 1. Architecture & Design

Kisima AI utilizes a modern, layered client-server architecture. The system separates user interface presentation, RESTful API routing, authoritative engineering logic, database persistence, and Retrieval-Augmented Generation (RAG) AI services.

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                            React Frontend                               │
 │                       TypeScript / Vite / Tailwind                      │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │ REST API (JSON / HTTP)
                                      ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                             FastAPI Backend                             │
 │                        API Routers & Middleware                         │
 └──────────────────┬──────────────────────────────────┬───────────────────┘
                    │                                  │
                    ▼                                  ▼
 ┌────────────────────────────────────┐  ┌─────────────────────────────────┐
 │   Deterministic Engine Layer       │  │          AI / RAG Layer         │
 │                                    │  │                                 │
 │ - Hazen-Williams Hydraulic Engine  │  │ - LangChain Pipeline            │
 │ - Sustainable Yield Abstraction    │  │ - ChromaDB Vector Embeddings    │
 │ - Pump Curve Interpolation (H-Q)   │  │ - LLM Provider (OpenAI/Mock)    │
 │ - Duty Point & Depth Suitability   │  │ - Manufacturer PDF Datasheets   │
 └──────────────────┬─────────────────┘  └─────────────────────────────────┘
                    │
                    ▼
 ┌────────────────────────────────────┐
 │        PostgreSQL Database         │
 │                                    │
 │ - Normalized `pumps` Table         │
 │ - `pump_curves` Head-Flow Data     │
 └────────────────────────────────────┘
```

## System Components

### 1. Frontend (React + TypeScript + Vite)
* Built with **React 19**, **TypeScript**, **Vite**, and **Tailwind CSS**.
* Provides a tabbed single-page workspace for selecting application modes (**Borehole** vs. **Well**), entering site parameters, displaying primary recommendations and alternative pumps, visualizing hydraulic loss breakdowns, rendering candidate rejection audits, and interacting with AI documentation assistance.
* Communicates asynchronously with the backend via standard `fetch` REST API clients defined in `src/services/api.ts`.

### 2. Backend REST API Layer (FastAPI)
* Implemented in Python using **FastAPI** (`backend/api/main.py`).
* Exposes structured RESTful JSON endpoints under `/api/v1`:
  * `POST /api/v1/recommendations/pump`: Executes hydraulic calculations and returns ranked pump recommendations.
  * `POST /api/v1/ai/explain`: Synthesizes customer-friendly technical explanations for recommended pumps.
  * `POST /api/v1/ai/ask`: Answers technical datasheet questions grounded in indexed manufacturer PDFs.
  * `GET /api/v1/pumps`: Lists indexed pump models with optional filtering.
  * `GET /api/v1/health`: Provides system and database connectivity health checks.

### 3. PostgreSQL Database & Repository Pattern
* Stores authoritative pump specifications (`pumps` table) and discrete head-flow-efficiency curve points (`pump_curves` table).
* Access is abstracted through the **Repository Pattern** (`PumpRepository`), decoupling database query logic from business rules and hydraulic evaluation services.

### 4. Authoritative Engineering Engine
* **Hydraulic Calculations**: Implements the Hazen-Williams equation in SI units ($h_f = 10.67 \cdot L \cdot Q^{1.852} / (C^{1.852} \cdot D^{4.871})$) for riser and delivery pipe friction head loss.
* **Sustainable Abstraction Protection**: Enforces an 80% sustainable yield factor rule ($Q_{sust} = Q_{yield} \times 0.80$) to protect aquifers from over-pumping.
* **Curve Interpolation & Evaluation**: Performs linear interpolation over discrete pump curve points to evaluate exact head capability and hydraulic efficiency at duty flow.
* **Appropriateness Filtering**: Enforces physical depth limits ($PSD \le MaxDepth$) and nominal flow class bounds ($\pm 40\%$ margin) to filter out under- or over-sized candidate pumps.

### 5. AI & RAG Knowledge Layer
* Built with **LangChain**, **ChromaDB**, and **LLM Abstraction** (`backend/ai/llm.py`).
* Manufacturer datasheets are chunked, embedded, and indexed in ChromaDB with metadata filters (`pump_family`, `family_prefix`).
* **Authoritative AI Grounding**: The deterministic engineering engine is strictly authoritative for sizing and recommendations. The LLM is restricted to synthesizing customer-friendly explanations and answering technical datasheet queries strictly grounded in retrieved RAG context.

## Architectural Patterns Present

* **Client-Server Architecture**: Clean separation between the browser single-page app and stateless FastAPI backend.
* **REST API Pattern**: Standard HTTP verbs (`GET`, `POST`), structured Pydantic schemas, and explicit JSON payload contracts.
* **Repository Pattern**: `PumpRepository` encapsulates PostgreSQL DDL, queries, and data mapping.
* **Separation of Concerns**: Hydraulic math (`engineering/`), business rules (`rules/`), evaluation logic (`selection/`), API contracts (`api/`), and AI synthesis (`ai/` & `rag/`) are kept in isolated modules.
* **Layered Architecture**: Flow of execution travels downward through API -> Service -> Rules/Engineering -> Repository/Data layers.
* **Retrieval-Augmented Generation (RAG)**: Combines vector similarity search over manufacturer PDFs with structured context injection for LLM prompts.

---

# 2. Testing Carried Out

Automated testing is critical for Kisima AI. In hydraulic engineering and water supply applications, incorrect calculations or improper pump selections can result in severe real-world consequences, including motor burnouts, inadequate water delivery, dry-running pump damage, or long-term aquifer depletion due to over-abstraction.

## Backend Automated Test Suite (Pytest)

The repository contains an extensive automated Pytest test suite in `backend/tests/`. Running `pytest backend/tests/` verifies **113 passed tests** across 9 test modules:

| Test Module | Tests | Description |
| :--- | :---: | :--- |
| `test_friction.py` | 7 | Verifies Hazen-Williams friction loss equations, flow rates, pipe diameters, materials, and fluid velocities. |
| `test_borehole.py` | 5 | Validates borehole input bounds, sustainable yield factors, and PSD vs. PWL rules. |
| `test_well.py` | 3 | Verifies well sizing defaults (e.g. 3.0 m³/h default flow, DSD pump family requirement). |
| `test_rules.py` | 23 | Tests 23 comprehensive borehole and well scenario rules (PWL as static head, PSD as riser length, 80% yield limit, delivery distance). |
| `test_selection.py` | 28 | Verifies pump curve interpolation, duty point head suitability, head margin calculation, depth checks, and ranking algorithms. |
| `test_importer.py` | 8 | Tests data import validation, schema initialization, duplicate detection, and enum parsing. |
| `test_rag.py` | 13 | Verifies PDF chunking, metadata extraction, strict pump family filtering (`DS`, `DSD`, `DSP`, `DSS`), RAG retrieval, and missing-context fallback answers. |
| `test_api.py` | 17 | Tests FastAPI REST endpoints (`/health`, `/recommendations/pump`, `/pumps`, `/pumps/{id}`) and Pydantic validation error handling. |
| `test_ai.py` | 9 | Tests `/api/v1/ai/explain` and `/api/v1/ai/ask` endpoints, LLM fallback handling, and source citation schemas. |
| **TOTAL** | **113 Passed** | **100% test pass rate across all backend modules (20.38s execution time).** |

## Frontend Build & Type Verification

The frontend production build process executes TypeScript type-checking (`tsc -b`) followed by Vite bundle optimization:

```bash
cd frontend
npm run build
```

**Verification Results:**
* **TypeScript Compilation**: Passed with 0 errors (`tsc -b`).
* **Vite Production Bundle**: Successfully built client bundle in `dist/` (1825 modules transformed in ~950ms).

---

# 3. Deployment Cost & Architecture Analysis

This section compares a **Managed Cloud Deployment** against an **On-Premises Deployment** for hosting Kisima AI in a production environment.

## 1. Managed Cloud Deployment

A managed cloud infrastructure utilizes Platform-as-a-Service (PaaS) and database cloud providers:

* **Frontend**: Hosted on **Vercel** or **Netlify** (Global CDN for static assets).
* **Backend API**: Hosted on **Render** or **Railway** (Python container runtime).
* **Database**: Managed **PostgreSQL** on Render, Supabase, or AWS RDS.
* **Vector Store**: Local persistent ChromaDB volume attached to backend container, or managed Pinecone / Qdrant.

### Cost Breakdown (Estimated Monthly)
* **Frontend Hosting (Vercel)**: Free Tier / $20/month per team seat.
* **Backend App Runtime (Render)**: $7 - $25/month (Standard Web Service with 1GB–2GB RAM).
* **Managed Database (Render PostgreSQL / Supabase)**: $7 - $15/month (Starter Managed DB with automatic backups).
* **LLM API Usage (OpenAI GPT-4o-mini)**: ~$5 - $20/month based on Q&A volume ($0.00015 / 1K tokens).
* **Total Estimated Cloud Cost**: **~$20 - $60 / month**

### Trade-Offs
* **Pros**: Zero hardware maintenance, automatic SSL certificates, global CDN edge caching, seamless CI/CD Git integration, high availability (99.9%+ uptime SLA), automated database snapshots.
* **Cons**: Recurring monthly operational expenditure, minor latency dependencies on external cloud providers.

---

## 2. On-Premises Deployment

An on-premises deployment involves installing Kisima AI on dedicated local server hardware within an enterprise or field station network.

### Hardware & Infrastructure Requirements
* **Server Hardware**: Dedicated mini-server or rack unit (e.g., 8-core CPU, 16GB RAM, 512GB NVMe SSD) — ~$1,200 initial capital expense.
* **Networking**: Gigabit router, firewall appliance, static public IP, network switch.
* **Power & Backup**: Uninterruptible Power Supply (UPS) battery unit + surge protection.
* **OS & Runtime**: Ubuntu Server LTS, Docker, Nginx reverse proxy, PostgreSQL server.

### Cost Breakdown (Estimated First-Year & Ongoing)
* **Initial Capital Expense (CapEx)**: ~$1,500 (Server, UPS, networking gear).
* **Electricity & Cooling**: ~$15 - $30 / month.
* **Internet Connection (Static IP)**: ~$50 - $100 / month.
* **Maintenance & System Administration**: Local IT staff time for OS security patches, database backups, and hardware failure replacements.
* **Total First-Year Cost**: **~$2,500 - $3,500** (~$80 - $150 / month ongoing thereafter).

### Trade-Offs
* **Pros**: Complete data sovereignty, full control over local network access, operational availability during internet outages (if run within a local LAN).
* **Cons**: High initial capital cost, single point of failure (hardware/power outages), manual security patch management, complex backup disaster recovery, high maintenance burden on local staff.

---

## Deployment Recommendation

For Kisima AI, a **Managed Cloud Deployment (Vercel + Render + Managed PostgreSQL)** is strongly recommended. It minimizes operational overhead, ensures continuous deployment via GitHub Actions CI/CD, provides automated scaling, and offers the lowest total cost of ownership (TCO) for field deployment.
