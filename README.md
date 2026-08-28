# Kisima AI

## AI-Assisted Borehole & Well Pump Sizing and Recommendation System

Kisima AI is an AI-assisted hydraulic engineering application designed to help engineers and water-system professionals size and select appropriate submersible borehole pumps.

The system combines a deterministic hydraulic engineering engine with manufacturer pump specifications, pump performance curves, PostgreSQL, and Retrieval-Augmented Generation (RAG) to produce technically grounded pump recommendations and manufacturer-documentation assistance.

> **Engineering-first architecture:** The deterministic engineering engine is authoritative for pump sizing and selection. AI is used to explain engineering results and answer questions from manufacturer documentation rather than independently determining pump suitability.

---

## Live Application

`[Insert Live Deployment URL Here]`

**GitHub Repository:** [https://github.com/MatoG50/kisima-ai]

---

## Project Management

`[https://trello.com/invite/b/6a8f551be11c51218a44d7f8/ATTI93a6be9ac6a10fb2db1c1dfd75417a77CF37C0AF/kisima-ai-msse-capstone]`

---

# 1. Project Overview

Pump selection for borehole and well water systems requires several engineering parameters to be considered simultaneously, including:

- Available borehole yield
- Pumping Water Level (PWL)
- Pump Setting Depth (PSD)
- Static lift
- Delivery distance
- Destination elevation
- Required flow
- Pipe friction losses
- Total Dynamic Head (TDH)
- Pump performance curves
- Pump operating range
- Sustainable borehole abstraction limits

Kisima AI automates this workflow by combining hydraulic calculations with manufacturer pump data and AI-assisted technical explanations.

The application evaluates available pump models against the calculated duty point and returns:

1. A primary recommended pump
2. Up to two suitable alternatives
3. Hydraulic calculation details
4. Pump curve operating information
5. Abstraction status
6. AI-generated technical explanation
7. Manufacturer documentation assistance through RAG

---

# 2. Key Features

## Hydraulic Pump Sizing

Kisima AI calculates the hydraulic requirements of a water system using engineering-based calculations.

The system evaluates:

- Static lift
- Riser pipe friction
- Delivery pipe friction
- Destination elevation
- Total Dynamic Head (TDH)
- Required operating flow
- Pump curve duty point

Hazen-Williams friction calculations are used for pipe-loss estimation.

---

## Sustainable Borehole Abstraction Protection

For borehole applications, Kisima AI protects against excessive abstraction.

The system evaluates the requested/design flow against the tested borehole yield and classifies the abstraction condition.

Possible states include:

- `SUSTAINABLE`
- `HIGH_ABSTRACTION`
- `EXCEEDS_YIELD`

The recommendation engine prevents pump selection where the required abstraction exceeds the permitted engineering limit.

---

## Pump Curve Evaluation

Manufacturer pump performance data is stored as normalized curve points and evaluated against the calculated hydraulic duty point.

The system uses pump curve interpolation to determine pump performance at the required operating flow.

Candidate pumps are evaluated based on:

- Available head
- Required TDH
- Operating flow
- Curve operating range
- Head margin
- Efficiency
- Pump depth limitations
- Other manufacturer specifications

---

## Appropriateness Filtering

Kisima AI does not simply select the pump with the highest available head.

The recommendation engine applies an appropriateness filter to avoid unsuitable oversized or poorly matched pumps.

The final API response provides:

- **1 recommended pump**
- **Up to 2 alternatives**

This keeps the result focused on pumps that are technically appropriate for the calculated duty point.

---

# 3. Application Modes

## Borehole

The borehole workflow uses:

- Tested borehole yield
- Pumping Water Level (PWL)
- Pump Setting Depth (PSD)
- Customer-required flow
- Delivery distance
- Destination elevation

The system applies sustainable abstraction protection and evaluates suitable submersible borehole pumps.

---

## Well

The well workflow is intended for shallow well or surface-water submersible applications where borehole drawdown information is not required.

The workflow uses:

- Static head
- Customer-required flow
- Delivery distance

The default candidate family is the DSD Series.

---

# 4. AI Capabilities

Kisima AI uses AI engineering techniques in two primary areas.

## AI Technical Explanation

After the deterministic engineering engine selects a pump, the AI explanation service converts the engineering output into a technical, customer-facing explanation.

The AI receives the authoritative engineering result rather than independently calculating the pump selection.

This separation helps prevent the language model from overriding engineering rules.

---

## Manufacturer AI Assistant

The Manufacturer AI Assistant provides conversational access to indexed manufacturer documentation.

Users can ask questions about topics such as:

- Pump materials
- Maximum immersion depth
- Electrical phase options
- Minimum borehole diameter
- Liquid compatibility
- Maximum liquid temperature
- Manufacturer specifications

The assistant uses Retrieval-Augmented Generation (RAG) to retrieve relevant manufacturer documentation from the vector database.

Responses include document citations where available.

### Grounding Strategy

The assistant is designed to:

1. Identify the relevant pump family/model from the question.
2. Retrieve relevant manufacturer documentation.
3. Restrict retrieval to the appropriate pump family where possible.
4. Provide answers based only on retrieved documentation.
5. Return an insufficient-context response when the available documentation does not support an answer.

This reduces the risk of presenting unsupported manufacturer specifications.

---

# 5. Future AI Copilot

A conversational hydraulic assistant is planned as a future enhancement.

The proposed Copilot will allow users to provide engineering requirements using natural language.

For example:

> "I need a pump for a borehole with a yield of 12 m³/h."

The future assistant could collect the required parameters conversationally and convert them into structured engineering inputs.

The deterministic sizing engine would then remain responsible for the actual hydraulic calculations and pump selection.

**Status: Coming Soon / Future Feature**

---

# 6. System Architecture & Tech Stack

Kisima AI follows a layered architecture separating the user interface, API layer, deterministic engineering logic, data storage, and AI/RAG services.

```text
                         ┌──────────────────────┐
                         │      React UI        │
                         │ TypeScript / Vite    │
                         │ Tailwind CSS         │
                         └──────────┬───────────┘
                                    │
                               REST API
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      API Layer       │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
       ┌──────────────────────┐              ┌──────────────────────┐
       │ Deterministic        │              │ AI / RAG Layer       │
       │ Engineering Engine   │              │                      │
       │                      │              │ LangChain            │
       │ Hydraulic Calculations│             │ Chroma               │
       │ Pump Selection       │              │ LLM                  │
       │ Curve Evaluation     │              │ Manufacturer PDFs    │
       └──────────┬───────────┘              └──────────────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ PostgreSQL           │
       │                      │
       │ Pump Specifications  │
       │ Pump Curve Data      │
       └──────────────────────┘
```

### Technology Stack
* **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons.
* **Backend API**: Python 3.11, FastAPI, Uvicorn, Pydantic v2.
* **Database**: PostgreSQL (`psycopg2-binary`).
* **Engineering Engine**: Python (Hazen-Williams SI equations, linear H-Q curve interpolation, sustainable abstraction rules).
* **AI & RAG Pipeline**: LangChain, ChromaDB vector embeddings, OpenAI GPT-4o-mini (with offline MockLLM fallback).
* **CI/CD**: GitHub Actions workflows for automated Pytest and Vite build verification.

---

# 7. Project Structure

```text
kisima-ai/
├── .github/
│   └── workflows/
│       └── main.yml            # GitHub Actions CI workflow
├── backend/
│   ├── ai/                     # RAG orchestration, prompts, and LLM abstraction
│   ├── api/                    # FastAPI routers, schema models, and endpoint handlers
│   ├── database/               # PostgreSQL connection factory and DDL schema
│   ├── engineering/            # Hazen-Williams friction, head, and hydraulic models
│   ├── models/                 # Dataclasses and enums (PumpModel, PhaseOptionEnum)
│   ├── rag/                    # PDF chunking, metadata extraction, and Chroma search
│   ├── repositories/           # PumpRepository data access layer
│   ├── rules/                  # Borehole and Well engineering business rules
│   ├── scripts/                # Database import and schema initialization scripts
│   ├── selection/              # Pump evaluation, curve interpolation, and ranking
│   ├── tests/                  # Pytest test suite (113 passing tests)
│   └── validation/             # Source data validation and integrity engine
├── data/
│   ├── documents/              # Manufacturer PDF datasheets
│   └── source/                 # Authoritative Excel specification and curve workbooks
├── docs/                       # Technical design and stage milestone reports
├── frontend/
│   ├── src/
│   │   ├── components/         # React workspace, layout, result, and modal components
│   │   ├── services/           # REST API fetch clients and TypeScript types
│   │   ├── App.tsx             # Root workspace state manager
│   │   └── main.tsx            # React application entry point
│   ├── package.json            # Node.js dependencies and build scripts
│   └── vite.config.ts          # Vite bundler configuration
├── Design_and_Testing.md       # MSSE Capstone system design and testing report
├── README.md                   # Project documentation
└── requirements.txt            # Python backend dependencies
```

---

# 8. Local Setup Instructions

Follow these instructions to clone and run Kisima AI on your local development machine.

### Prerequisites
* **Python**: `3.10` or `3.11`
* **Node.js**: `v18` or `v20+`
* **PostgreSQL**: `v14+` running locally or via Docker
* **Git**

---

### Backend Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/MatoG50/kisima-ai.git
   cd kisima-ai
   ```

2. **Create and Activate a Python Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy `.env.example` to `.env` or export the variables in your terminal:
   ```bash
   cp .env.example .env
   ```

   Default environment configuration:
   ```ini
   POSTGRES_DB=capstone_pump_db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   OPENAI_API_KEY=your_openai_api_key_here # Optional: MockLLM is used if omitted
   LLM_PROVIDER=auto
   ```

5. **Initialize Database Schema & Ingest Source Data:**
   Ensure PostgreSQL is running and the target database exists, then initialize tables and ingest pump curve data:
   ```bash
   python3 backend/scripts/import_pumps.py --init-db
   ```

6. **Run Backend REST API Server:**
   ```bash
   uvicorn backend.api.main:app --reload --port 8000
   ```
   The API interactive documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

### Frontend Setup

1. **Navigate to the Frontend Directory:**
   ```bash
   cd frontend
   ```

2. **Install Frontend Dependencies:**
   ```bash
   npm install
   ```

3. **Run the Frontend Development Server:**
   ```bash
   npm run dev
   ```
   The application UI will open at [http://localhost:5173](http://localhost:5173).

---

### Running Tests & Building

* **Run Backend Pytest Suite:**
  ```bash
  python3 -m pytest backend/tests/ -v
  ```

* **Run Production Frontend Build:**
  ```bash
  cd frontend
  npm run build
  ```

---

# 9. Deployment Overview

Kisima AI is designed for containerized or PaaS cloud deployment:

* **Frontend**: Can be built into static assets (`dist/`) and deployed to Vercel, Netlify, or AWS S3/CloudFront.
* **Backend API**: Can be deployed to Render, Railway, or AWS App Runner using `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`.
* **Database**: Uses managed PostgreSQL (Render Postgres, Supabase, or AWS RDS).
* **CI/CD Pipeline**: GitHub Actions automatically runs backend tests (`pytest backend/tests/`) and frontend build checks (`npm run build`) on every push to `main`.