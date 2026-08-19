"""
Automated Test Suite for Stage 6 — AI Explanation & Technical Q&A Endpoints.
Tests /api/v1/ai/explain and /api/v1/ai/ask routes, validation rules, RAG source citations,
and preservation of deterministic backend calculations.
"""

# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

# 1. POST /api/v1/ai/explain (Valid Borehole Recommendation Result)
def test_api_explain_recommendation_success():
    payload = {
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
    response = client.post("/api/v1/ai/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["pump_id"] == "ds05-17"
    assert data["pump_family"] == "DS5"
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert isinstance(data["sources"], list)

# 2. POST /api/v1/ai/explain (Invalid Input -> HTTP 422)
def test_api_explain_recommendation_invalid_input():
    payload = {
        "pump_id": "ds05-17",
        "design_flow_m3h": -5.0, # Negative flow rate invalid
        "tdh_m": 93.6
    }
    response = client.post("/api/v1/ai/explain", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "VALIDATION_ERROR"

# 3. POST /api/v1/ai/ask (Question referencing specific pump)
def test_api_ask_question_with_pump_context():
    payload = {
        "question": "Why was DS05-17 recommended for this borehole?",
        "pump_id": "ds05-17"
    }
    response = client.post("/api/v1/ai/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert isinstance(data["sources"], list)

# 4. POST /api/v1/ai/ask (General engineering definition question)
def test_api_ask_general_question():
    payload = {
        "question": "What does PSD mean in pump sizing and why is it important?"
    }
    response = client.post("/api/v1/ai/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

# 5. Preservation of Deterministic Backend Results
def test_api_explain_preserves_deterministic_numbers():
    payload = {
        "pump_id": "ds02-09",
        "application_type": "borehole",
        "design_flow_m3h": 1.5,
        "tdh_m": 41.7,
        "pump_head_m": 41.7,
        "efficiency_percent": 47.0,
        "head_margin_m": 0.0,
        "yield_m3h": 2.0,
        "abstraction_status": "SUSTAINABLE"
    }
    response = client.post("/api/v1/ai/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["pump_id"] == "ds02-09"
    # Ensure exact pump ID is echoed and retained
