# AI-Powered Pump & Solar Sizing Backend

Backend engineering data pipeline, hydraulic calculations database, and RAG retrieval infrastructure for solar pump sizing.

---

## Stage 2 — Excel to PostgreSQL Data Pipeline

Stage 2 establishes the normalized PostgreSQL database for the pump sizing application and executes an idempotent, validated import of manufacturer specification and performance curve data from Excel workbooks (`pump_models.xlsx` and `pump_curves.xlsx`).

---

## Directory Architecture

```
capstone-backend/
├── data/
│   └── source/
│       ├── pump_models.xlsx   # Authoritative source pump specifications
│       └── pump_curves.xlsx   # Authoritative source performance curve points
├── backend/
│   ├── database/
│   │   ├── connection.py      # PostgreSQL connection factory and DDL initializer
│   │   └── schema.sql         # PostgreSQL DDL schema definition
│   ├── models/
│   │   └── pump.py            # Dataclasses and PhaseOptionEnum definitions
│   ├── validation/
│   │   └── validator.py       # Data validation & relationship integrity engine
│   ├── repositories/
│   │   └── pump_repository.py # Idempotent bulk upsert repository
│   ├── scripts/
│   │   └── import_pumps.py    # Main CLI importer & report generator
│   └── tests/
│       └── test_importer.py   # Automated pytest unit test suite
├── README.md
└── requirements.txt
```

---

## Environment & Configuration

Set the following environment variables to configure PostgreSQL database connection details:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `POSTGRES_DB` | `capstone_pump_db` | PostgreSQL Database Name |
| `POSTGRES_USER` | `postgres` | Database User |
| `POSTGRES_PASSWORD` | `postgres` | Database Password |
| `POSTGRES_HOST` | `localhost` | Database Host |
| `POSTGRES_PORT` | `5432` | Database Port |

---

## Setup & Running the Pipeline

### 1. Install Dependencies
```bash
python3 -m pip install openpyxl pandas psycopg2-binary pytest
```

### 2. Run Automated Unit Tests
```bash
python3 -m pytest backend/tests/
```

### 3. Run Dry-Run Data Validation
To validate source Excel data without connecting to PostgreSQL:
```bash
python3 backend/scripts/import_pumps.py --dry-run
```

### 4. Initialize Database Schema & Ingest Data into PostgreSQL
Ensure PostgreSQL is running, then execute:
```bash
python3 backend/scripts/import_pumps.py --init-db
```

To re-run the importer idempotently (updates existing records without duplication):
```bash
python3 backend/scripts/import_pumps.py
```

---

## PostgreSQL Database Schema Summary

### Table: `pumps`
* `pump_id` (`VARCHAR(50)`, Primary Key) — Lowercase canonical pump identifier.
* `pump_name` (`VARCHAR(100)`) — Commercial pump model designation.
* `motor_kw` (`NUMERIC(5,2)`) — Nominal motor output power rating ($\text{kW}$).
* `max_depth_m` (`NUMERIC(6,2)`) — Maximum immersion depth / submersion head ($\text{m}$).
* `phase_option` (`electrical_phase_enum`: `'1PH'`, `'3PH'`, `'1PH_3PH'`) — Electrical phase availability.
* `flc_1ph_a` (`NUMERIC(5,2)`, Nullable) — Full Load Current at single-phase 1x240V ($\text{A}$).
* `flc_3ph_a` (`NUMERIC(5,2)`, Nullable) — Full Load Current at three-phase 3x415V ($\text{A}$).
* `discharge_size_in` (`NUMERIC(4,2)`) — Pump outlet diameter ($\text{in}$).
* `raw_pump_id` (`VARCHAR(50)`) — Original extracted ID for traceability.
* `created_at`, `updated_at` (`TIMESTAMPTZ`).

### Table: `pump_curves`
* `id` (`BIGINT`, Primary Key, Identity).
* `pump_id` (`VARCHAR(50)`, Foreign Key $\rightarrow$ `pumps.pump_id` `ON DELETE CASCADE`).
* `flow_m3h` (`NUMERIC(6,2)`) — Volumetric flow rate ($\text{m}^3/\text{h}$).
* `head_m` (`NUMERIC(6,2)`) — Total Dynamic Head ($\text{m}$).
* `efficiency_percent` (`NUMERIC(5,2)`) — Hydraulic efficiency ($\%$).
* `created_at`, `updated_at` (`TIMESTAMPTZ`).
* Constraint: `UNIQUE(pump_id, flow_m3h)` enforcing unique curve points per flow coordinate.
