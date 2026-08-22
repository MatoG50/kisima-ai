"""
Automated Test Suite for Stage 5 — Backend REST API Layer.
Uses FastAPI TestClient to test health checks, pump listing, filtering, single pump curves,
borehole & well recommendations, input validation, error handling, and response structures.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

# 1. GET /api/v1/health
def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data

# 2. GET /api/v1/pumps (list all pumps)
def test_api_list_pumps():
    response = client.get("/api/v1/pumps")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "pumps" in data
    assert data["total_count"] > 0
    assert len(data["pumps"]) == data["total_count"]
    # Check structure of first pump item
    p0 = data["pumps"][0]
    assert "pump_id" in p0
    assert "pump_name" in p0
    assert "motor_kw" in p0
    assert "max_depth_m" in p0
    assert "phase_option" in p0
    assert "discharge_size_in" in p0

# 3. GET /api/v1/pumps with family & motor_kw filters
def test_api_list_pumps_filtering():
    response = client.get("/api/v1/pumps?pump_family=dsd&min_motor_kw=1.0&max_motor_kw=3.0")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] > 0
    for p in data["pumps"]:
        assert "dsd" in p["pump_id"].lower()
        assert 1.0 <= p["motor_kw"] <= 3.0

# 4. GET /api/v1/pumps/{pump_id} existing pump
def test_api_get_existing_pump_detail():
    response = client.get("/api/v1/pumps/ds05-17")
    assert response.status_code == 200
    data = response.json()
    assert data["pump_id"] == "ds05-17"
    assert data["pump_name"] == "dayliff ds5/17"
    assert data["motor_kw"] == 1.5
    assert "curve" in data
    assert len(data["curve"]) > 0
    pt0 = data["curve"][0]
    assert "flow_m3h" in pt0
    assert "head_m" in pt0
    assert "efficiency_percent" in pt0

# 5. GET /api/v1/pumps/{pump_id} nonexistent pump -> 404
def test_api_get_nonexistent_pump_404():
    response = client.get("/api/v1/pumps/nonexistent-pump-xyz")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

# 6. POST /api/v1/recommendations/pump (Borehole Sustainable Flow)
def test_api_recommendation_borehole_sustainable():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 40.0,
        "psd_m": 80.0,
        "delivery_distance_m": 100.0,
        "destination_elevation_m": 5.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["application_type"] == "borehole"
    assert data["design_flow_m3h"] == 8.0
    assert data["abstraction_status"] == "SUSTAINABLE"
    assert data["recommended_pump"] is not None
    assert data["recommended_pump"]["pump_id"] is not None
    assert data["recommended_pump"]["hydraulic_result"] is not None
    assert isinstance(data["alternatives"], list)

# 7. POST /api/v1/recommendations/pump (Well Default 3.0 m3/h)
def test_api_recommendation_well_default():
    payload = {
        "application_type": "well",
        "static_head_m": 20.0,
        "delivery_distance_m": 50.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["application_type"] == "well"
    assert data["design_flow_m3h"] == 3.0
    assert data["recommended_pump"] is not None
    assert "dsd" in data["recommended_pump"]["pump_id"].lower()

# 8. POST /api/v1/recommendations/pump (Borehole High Abstraction Warning)
def test_api_recommendation_borehole_high_abstraction():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 40.0,
        "psd_m": 80.0,
        "customer_requested_flow_m3h": 9.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["abstraction_status"] == "HIGH_ABSTRACTION"
    assert len(data["warnings"]) > 0

# 9. POST /api/v1/recommendations/pump (Borehole Above Yield Warning)
def test_api_recommendation_borehole_exceeds_yield_warning():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 40.0,
        "psd_m": 80.0,
        "customer_requested_flow_m3h": 12.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["recommended_pump"] is not None
    assert any("High-abstraction operation" in w for w in data["warnings"])

# 10. POST /api/v1/recommendations/pump (No Suitable Pump)
def test_api_recommendation_no_suitable_pump():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 400.0,
        "psd_m": 450.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NO_SUITABLE_PUMP"
    assert data["recommended_pump"] is None
    assert data["rejection_summary"]["viable_candidates_count"] == 0

# 11. POST /api/v1/recommendations/pump (Invalid Input -> HTTP 422)
def test_api_recommendation_invalid_input_validation():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 50.0,
        "psd_m": 30.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "VALIDATION_ERROR"
    assert "details" in data

# 12. POST /api/v1/recommendations/pump (Customer Flow Override)
def test_api_recommendation_customer_flow_override():
    payload = {
        "application_type": "well",
        "static_head_m": 25.0,
        "customer_requested_flow_m3h": 5.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["design_flow_m3h"] == 5.0

# 13. Response Structure Verification
def test_api_response_structure():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 30.0,
        "psd_m": 50.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    rec = data["recommended_pump"]
    assert "pump_id" in rec
    assert "pump_name" in rec
    assert "motor_kw" in rec
    assert "discharge_size_in" in rec
    assert "max_depth_m" in rec
    assert "required_tdh_m" in rec
    assert "pump_head_at_design_flow_m" in rec
    assert "head_margin_m" in rec
    assert "operating_efficiency_percent" in rec
    assert "suitability_score" in rec
    
    hyd = rec["hydraulic_result"]
    assert "static_head_m" in hyd
    assert "riser_friction_m" in hyd
    assert "delivery_friction_m" in hyd
    assert "total_dynamic_head_m" in hyd
    assert "riser_pipe_quantity" in hyd
    assert "velocity_m_s" in hyd

# 14. CORS Headers Verification
def test_api_cors_headers():
    response = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

# 15. Zero requested flow defaults to None coercion
def test_api_recommendation_zero_requested_flow():
    payload = {
        "application_type": "borehole",
        "yield_m3h": 10.0,
        "pwl_m": 30.0,
        "psd_m": 50.0,
        "customer_requested_flow_m3h": 0.0
    }
    response = client.post("/api/v1/recommendations/pump", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["design_flow_m3h"] == 8.0 # Coerced to None, so uses 80% sustainable flow (8.0)
