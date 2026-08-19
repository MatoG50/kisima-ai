# Stage 5 — Backend REST API Layer Report

## 1. Executive Summary

Stage 5 has successfully implemented a thin, production-ready FastAPI REST API layer for the pump-sizing backend.

The API exposes the existing Stage 1–4 PostgreSQL database (`capstone_pump_db`) and deterministic engineering engine under the `/api/v1/` route prefix. The API layer is strictly thin: all hydraulic calculations, curve interpolations, ranking algorithms, and yield rules remain inside the underlying domain/service modules.

Interactive OpenAPI/Swagger documentation is automatically served at `/docs` and `/redoc`.

---

## 2. Directory Architecture & Implemented Modules

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, lifespan, CORS, global error handlers
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /api/v1/health
│   │   ├── pumps.py         # GET /api/v1/pumps, GET /api/v1/pumps/{pump_id}
│   │   └── recommendations.py # POST /api/v1/recommendations/pump
│   └── schemas/
│       ├── __init__.py
│       ├── pump.py          # Pydantic schemas for pump metadata & curves
│       └── recommendation.py # Pydantic schemas for request validation & responses
├── engineering/             # Deterministic physical calculations (Unchanged)
├── rules/                   # Business logic & yield rules (Unchanged)
├── selection/               # Candidate interpolation, scoring & recommendation (Unchanged)
├── repositories/            # PostgreSQL data access layer
├── database/                # Connection factory
├── tests/
│   ├── test_api.py          # FastAPI TestClient automated unit tests
│   └── ...                  # (77 existing tests)
├── .env.example             # Environment variable template
└── docs/
    └── stage_5_report.md    # Stage 5 REST API Documentation & OpenAPI specs
```

---

## 3. Endpoints & API Specifications

### 3.1 `GET /api/v1/health`
Checks API operational status and PostgreSQL database connectivity.

* **Response Example**:
  ```json
  {
    "status": "ok",
    "database": "connected"
  }
  ```

* **cURL Example**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/health
  ```

---

### 3.2 `GET /api/v1/pumps`
Queries PostgreSQL pump metadata records with optional query parameters.

* **Query Parameters**:
  * `application_type` (`string`, optional): `'borehole'` or `'well'` (filters DSD family for well).
  * `pump_family` (`string`, optional): e.g. `'dsd'`, `'ds'`.
  * `phase` (`string`, optional): `'1PH'`, `'3PH'`, `'1PH_3PH'`.
  * `min_motor_kw` (`float`, optional): Minimum motor power in kW.
  * `max_motor_kw` (`float`, optional): Maximum motor power in kW.

* **Response Example**:
  ```json
  {
    "total_count": 151,
    "pumps": [
      {
        "pump_id": "ds02-09",
        "pump_name": "dayliff ds2/9",
        "motor_kw": 0.37,
        "max_depth_m": 200.0,
        "phase_option": "1PH",
        "flc_1ph_a": 9.0,
        "flc_3ph_a": null,
        "discharge_size_in": 1.25,
        "raw_pump_id": "ds02-09"
      }
    ]
  }
  ```

* **cURL Example**:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/pumps?pump_family=dsd&min_motor_kw=1.0&max_motor_kw=3.0"
  ```

---

### 3.3 `GET /api/v1/pumps/{pump_id}`
Retrieves metadata and full performance curve array for a single pump model.

* **Path Parameters**: `pump_id` (e.g. `ds05-17`).
* **HTTP 404**: Returned if `pump_id` is not found.

* **Response Example**:
  ```json
  {
    "pump_id": "ds05-17",
    "pump_name": "dayliff ds5/17",
    "motor_kw": 1.5,
    "max_depth_m": 200.0,
    "phase_option": "1PH_3PH",
    "flc_1ph_a": 35.0,
    "flc_3ph_a": 20.0,
    "discharge_size_in": 1.5,
    "raw_pump_id": "ds05-17",
    "curve": [
      { "flow_m3h": 0.0, "head_m": 105.0, "efficiency_percent": 1.5 },
      { "flow_m3h": 1.0, "head_m": 104.0, "efficiency_percent": 22.0 },
      { "flow_m3h": 5.0, "head_m": 89.2, "efficiency_percent": 64.5 }
    ]
  }
  ```

* **cURL Example**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/pumps/ds05-17
  ```

---

### 3.4 `POST /api/v1/recommendations/pump`
Primary recommendation endpoint consuming engineering requirements and executing candidate evaluation.

#### Request Schemas

##### Borehole Request:
```json
{
  "application_type": "borehole",
  "yield_m3h": 10.0,
  "pwl_m": 40.0,
  "psd_m": 80.0,
  "delivery_distance_m": 100.0,
  "destination_elevation_m": 5.0,
  "customer_requested_flow_m3h": null
}
```

##### Well Request:
```json
{
  "application_type": "well",
  "static_head_m": 20.0,
  "delivery_distance_m": 50.0,
  "destination_elevation_m": 0.0,
  "customer_requested_flow_m3h": null
}
```

#### Response Example (Sustainable Borehole):
```json
{
  "status": "SUCCESS",
  "application_type": "borehole",
  "design_flow_m3h": 8.0,
  "abstraction_status": "SUSTAINABLE",
  "yield_m3h": 10.0,
  "pwl_m": 40.0,
  "psd_m": 80.0,
  "destination_elevation_m": 5.0,
  "delivery_distance_m": 100.0,
  "warnings": [],
  "recommended_pump": {
    "pump_id": "ds05-17",
    "pump_name": "dayliff ds5/17",
    "motor_kw": 1.5,
    "max_depth_m": 200.0,
    "phase_option": "1PH_3PH",
    "flc_1ph_a": 35.0,
    "flc_3ph_a": 20.0,
    "discharge_size_in": 1.5,
    "design_flow_m3h": 8.0,
    "required_tdh_m": 93.577,
    "pump_head_at_design_flow_m": 89.20,
    "head_margin_m": 4.62,
    "operating_efficiency_percent": 64.50,
    "suitability_score": 92.40,
    "hydraulic_result": {
      "static_head_m": 45.0,
      "riser_length_m": 80.0,
      "riser_friction_m": 20.063,
      "delivery_length_m": 100.0,
      "delivery_friction_m": 28.514,
      "total_dynamic_head_m": 93.577,
      "riser_pipe_quantity": 27,
      "standard_riser_length_m": 3.0,
      "riser_material": "uPVC",
      "delivery_material": "HDPE",
      "pipe_diameter_in": 1.5,
      "velocity_m_s": 1.95
    }
  },
  "alternatives": [ ... ],
  "rejection_summary": {
    "total_candidates_evaluated": 151,
    "viable_candidates_count": 12,
    "rejected_depth_exceeded": 0,
    "rejected_out_of_range": 85,
    "rejected_insufficient_head": 54
  }
}
```

* **cURL Example**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/recommendations/pump \
    -H "Content-Type: application/json" \
    -d '{
      "application_type": "borehole",
      "yield_m3h": 10.0,
      "pwl_m": 40.0,
      "psd_m": 80.0,
      "delivery_distance_m": 100.0,
      "destination_elevation_m": 5.0
    }'
  ```

---

## 4. Input Validation & Error Handling

### 4.1 Input Validation Rules (HTTP 422)
Pydantic v2 schemas reject malformed requests:
* `yield_m3h <= 0` for borehole requests.
* `pwl_m < 0` or `psd_m <= 0` for borehole requests.
* `psd_m < pwl_m` (PSD shallower than water level).
* Negative delivery distances or customer flow rates.

**Validation Error Response (HTTP 422)**:
```json
{
  "status": "VALIDATION_ERROR",
  "message": "Invalid request payload or engineering input parameter.",
  "details": [
    "Field 'psd_m': Pump Setting Depth (psd_m=30.0m) cannot be shallower than Pumping Water Level (pwl_m=50.0m)."
  ]
}
```

### 4.2 Application Level Engineering Outcomes (HTTP 200)
Valid engineering requests where no pump is capable or where abstraction rules reject the flow return HTTP 200 with structured JSON:
* **`EXCEEDS_YIELD`**: Requested customer flow exceeds tested borehole yield.
* **`NO_SUITABLE_PUMP`**: Duty point exceeds capability of all candidate pumps in database.

---

## 5. CORS & Environment Configuration

CORS origins are configured via environment variable `API_CORS_ORIGINS`:

```bash
# .env file
POSTGRES_DB=capstone_pump_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

API_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

---

## 6. Test Suite Execution & Coverage

All 91 automated unit tests across Stages 2–5 passed cleanly:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/MGK/Documents/projects/capstone-backend
plugins: anyio-4.12.1
collected 91 items

backend/tests/test_api.py ..............                                 [ 15%]
backend/tests/test_borehole.py ..........                                [ 26%]
backend/tests/test_friction.py .......                                   [ 34%]
backend/tests/test_importer.py ........                                  [ 42%]
backend/tests/test_rules.py .......................                      [ 68%]
backend/tests/test_selection.py ..........................               [ 96%]
backend/tests/test_well.py ...                                           [100%]

======================== 91 passed, 1 warning in 2.69s =========================
```

---

Stage 5 complete — backend REST API layer is running locally, tested, and documented. Ready for user review.
