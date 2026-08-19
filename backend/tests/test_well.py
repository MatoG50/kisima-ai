"""
Test Suite for Well Application Business Rules.
"""

# pyrefly: ignore [missing-import]
import pytest
from backend.rules.well import evaluate_well_application

def test_well_default_flow_3m3h():
    res = evaluate_well_application(static_head_m=20.0)
    assert res.design_flow_m3h == 3.0
    assert res.is_default_flow_used is True
    assert res.default_pump_family == "DSD"

def test_well_customer_flow_override():
    res = evaluate_well_application(static_head_m=20.0, customer_requested_flow_m3h=5.5)
    assert res.design_flow_m3h == 5.5
    assert res.is_default_flow_used is False

def test_well_hydraulics_with_delivery_distance():
    res = evaluate_well_application(
        static_head_m=30.0,
        customer_requested_flow_m3h=3.0,
        delivery_distance_m=100.0,
        pipe_diameter_in=1.25
    )
    assert res.hydraulic_result is not None
    assert res.hydraulic_result.static_head_m == 30.0
    assert res.hydraulic_result.delivery_length_m == 100.0
    assert res.hydraulic_result.delivery_friction_m > 0.0
    assert res.hydraulic_result.total_dynamic_head_m > 30.0
