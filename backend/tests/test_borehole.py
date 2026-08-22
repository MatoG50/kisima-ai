"""
Test Suite for Borehole Application Business Rules and Head Calculations.
"""

# pyrefly: ignore [missing-import]
import pytest
from backend.engineering.head import calculate_static_head, calculate_riser_pipe_quantity
from backend.rules.borehole import evaluate_borehole_application, evaluate_pump_depth_suitability
from backend.engineering.results import AbstractionStatusEnum

def test_pwl_used_as_hydraulic_head():
    # PWL = 60m, elevation = 10m -> static head = 70m
    static_head = calculate_static_head(pwl_m=60.0, destination_elevation_m=10.0)
    assert static_head == 70.0

def test_psd_not_used_as_hydraulic_head():
    # Increasing PSD from 80m to 120m while keeping PWL=60m and elevation=0m MUST NOT change static head
    res_80m = evaluate_borehole_application(yield_m3h=10.0, pwl_m=60.0, psd_m=80.0, pipe_diameter_in=2.0)
    res_120m = evaluate_borehole_application(yield_m3h=10.0, pwl_m=60.0, psd_m=120.0, pipe_diameter_in=2.0)
    
    assert res_80m.hydraulic_result.static_head_m == 60.0
    assert res_120m.hydraulic_result.static_head_m == 60.0
    # Riser friction length DOES change with PSD
    assert res_80m.hydraulic_result.riser_length_m == 80.0
    assert res_120m.hydraulic_result.riser_length_m == 120.0

def test_psd_riser_pipe_quantity_calculation():
    # 90m PSD / 3.0m = 30 pipes exactly
    assert calculate_riser_pipe_quantity(psd_m=90.0, standard_riser_length_m=3.0) == 30
    # 91m PSD / 3.0m = 30.33 -> 31 pipes
    assert calculate_riser_pipe_quantity(psd_m=91.0, standard_riser_length_m=3.0) == 31

def test_80_percent_sustainable_yield_rule():
    # Yield = 10 m3/h -> default design flow = 8.0 m3/h
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0)
    assert res.sustainable_flow_m3h == 8.0
    assert res.design_flow_m3h == 8.0
    assert res.abstraction_status == AbstractionStatusEnum.SUSTAINABLE

def test_customer_flow_below_80_percent_yield():
    # Yield = 10 m3/h, requested = 5 m3/h (5 <= 8) -> SUSTAINABLE
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0, customer_requested_flow_m3h=5.0)
    assert res.design_flow_m3h == 5.0
    assert res.abstraction_status == AbstractionStatusEnum.SUSTAINABLE
    assert res.warning_message is None

def test_customer_flow_exactly_80_percent_yield():
    # Yield = 10 m3/h, requested = 8 m3/h -> SUSTAINABLE
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0, customer_requested_flow_m3h=8.0)
    assert res.design_flow_m3h == 8.0
    assert res.abstraction_status == AbstractionStatusEnum.SUSTAINABLE

def test_customer_flow_above_80_percent_below_yield():
    # Yield = 10 m3/h, requested = 9 m3/h (8 < 9 < 10) -> HIGH_ABSTRACTION
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0, customer_requested_flow_m3h=9.0)
    assert res.design_flow_m3h == 9.0
    assert res.abstraction_status == AbstractionStatusEnum.HIGH_ABSTRACTION
    assert res.warning_message is not None
    assert "above the recommended 80%" in res.warning_message

def test_customer_flow_equal_to_yield():
    # Yield = 10 m3/h, requested = 10 m3/h -> EXCEEDS_YIELD with warning
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0, customer_requested_flow_m3h=10.0)
    assert res.design_flow_m3h == 10.0
    assert res.abstraction_status == AbstractionStatusEnum.EXCEEDS_YIELD
    assert "High-abstraction operation" in res.warning_message

def test_customer_flow_above_yield_warning():
    # Yield = 10 m3/h, requested = 12 m3/h (12 > 10) -> EXCEEDS_YIELD with warning
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=50.0, psd_m=80.0, customer_requested_flow_m3h=12.0)
    assert res.abstraction_status == AbstractionStatusEnum.EXCEEDS_YIELD
    assert res.error_message is None
    assert "High-abstraction operation" in res.warning_message

def test_pump_max_depth_suitability():
    # PSD = 150m, pump max_depth = 200m -> suitable
    assert evaluate_pump_depth_suitability(psd_m=150.0, pump_max_depth_m=200.0) is True
    # PSD = 250m, pump max_depth = 200m -> unsuitable
    assert evaluate_pump_depth_suitability(psd_m=250.0, pump_max_depth_m=200.0) is False
