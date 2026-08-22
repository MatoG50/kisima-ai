"""
Comprehensive Test Suite for All 23 Stage 3 Engineering & Rule Scenarios.
"""

# pyrefly: ignore [missing-import]
import pytest
from backend.engineering.units import inches_to_meters, m3h_to_m3s
from backend.engineering.materials import get_pipe_material
from backend.engineering.friction import calculate_hazen_williams_friction
from backend.engineering.head import calculate_static_head, calculate_riser_pipe_quantity
from backend.rules.validation import validate_borehole_inputs, EngineeringValidationError
from backend.rules.borehole import evaluate_borehole_application, evaluate_pump_depth_suitability
from backend.rules.well import evaluate_well_application
from backend.engineering.results import AbstractionStatusEnum

# 1. PWL used as hydraulic head
def test_scenario_01_pwl_used_as_hydraulic_head():
    head = calculate_static_head(pwl_m=45.0, destination_elevation_m=5.0)
    assert head == 50.0

# 2. PSD NOT used as hydraulic head
def test_scenario_02_psd_not_used_as_hydraulic_head():
    res_psd50 = evaluate_borehole_application(yield_m3h=10.0, pwl_m=30.0, psd_m=50.0, pipe_diameter_in=2.0)
    res_psd100 = evaluate_borehole_application(yield_m3h=10.0, pwl_m=30.0, psd_m=100.0, pipe_diameter_in=2.0)
    assert res_psd50.hydraulic_result.static_head_m == 30.0
    assert res_psd100.hydraulic_result.static_head_m == 30.0

# 3. PSD used as riser length
def test_scenario_03_psd_used_as_riser_length():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=30.0, psd_m=75.0, pipe_diameter_in=2.0)
    assert res.hydraulic_result.riser_length_m == 75.0

# 4. PSD maximum-depth validation
def test_scenario_04_psd_max_depth_validation():
    assert evaluate_pump_depth_suitability(psd_m=180.0, pump_max_depth_m=200.0) is True
    assert evaluate_pump_depth_suitability(psd_m=220.0, pump_max_depth_m=200.0) is False

# 5. 80% yield rule
def test_scenario_05_80_percent_yield_rule():
    res = evaluate_borehole_application(yield_m3h=15.0, pwl_m=20.0, psd_m=30.0)
    assert res.sustainable_flow_m3h == 12.0
    assert res.design_flow_m3h == 12.0

# 6. Customer flow below 80% yield
def test_scenario_06_customer_flow_below_80_percent_yield():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=20.0, psd_m=30.0, customer_requested_flow_m3h=6.0)
    assert res.abstraction_status == AbstractionStatusEnum.SUSTAINABLE

# 7. Customer flow exactly 80% yield
def test_scenario_07_customer_flow_exactly_80_percent_yield():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=20.0, psd_m=30.0, customer_requested_flow_m3h=8.0)
    assert res.abstraction_status == AbstractionStatusEnum.SUSTAINABLE

# 8. Customer flow above 80% but below yield
def test_scenario_08_customer_flow_above_80_percent_below_yield():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=20.0, psd_m=30.0, customer_requested_flow_m3h=9.0)
    assert res.abstraction_status == AbstractionStatusEnum.HIGH_ABSTRACTION
    assert res.warning_message is not None

# 9. Customer flow equal to yield
def test_scenario_09_customer_flow_equal_to_yield():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=20.0, psd_m=30.0, customer_requested_flow_m3h=10.0)
    assert res.abstraction_status == AbstractionStatusEnum.EXCEEDS_YIELD
    assert "High-abstraction operation" in res.warning_message

# 10. Customer flow above yield -> warning (no rejection)
def test_scenario_10_customer_flow_above_yield_warning():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=20.0, psd_m=30.0, customer_requested_flow_m3h=11.0)
    assert res.abstraction_status == AbstractionStatusEnum.EXCEEDS_YIELD
    assert res.error_message is None
    assert "High-abstraction operation" in res.warning_message

# 11. Well default flow = 3 m3/h
def test_scenario_11_well_default_flow_3m3h():
    res = evaluate_well_application(static_head_m=15.0)
    assert res.design_flow_m3h == 3.0
    assert res.is_default_flow_used is True

# 12. Well customer flow override
def test_scenario_12_well_customer_flow_override():
    res = evaluate_well_application(static_head_m=15.0, customer_requested_flow_m3h=4.2)
    assert res.design_flow_m3h == 4.2
    assert res.is_default_flow_used is False

# 13. Riser friction
def test_scenario_13_riser_friction():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, pipe_diameter_in=2.0)
    assert res.hydraulic_result.riser_friction_m > 0.0

# 14. Delivery friction
def test_scenario_14_delivery_friction():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, delivery_distance_m=150.0, pipe_diameter_in=2.0)
    assert res.hydraulic_result.delivery_friction_m > 0.0

# 15. No delivery distance
def test_scenario_15_no_delivery_distance():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, delivery_distance_m=0.0, pipe_diameter_in=2.0)
    assert res.hydraulic_result.delivery_friction_m == 0.0

# 16. Destination elevation
def test_scenario_16_destination_elevation():
    res = evaluate_borehole_application(yield_m3h=10.0, pwl_m=40.0, psd_m=80.0, destination_elevation_m=12.5, pipe_diameter_in=2.0)
    assert res.hydraulic_result.static_head_m == 52.5

# 17. Pipe material selection
def test_scenario_17_pipe_material_selection():
    mat_upvc = get_pipe_material("uPVC")
    mat_hdpe = get_pipe_material("HDPE")
    assert mat_upvc.hazen_williams_c == 150.0
    assert mat_hdpe.hazen_williams_c == 140.0

# 18. Pipe diameter effects
def test_scenario_18_pipe_diameter_effects():
    hf_1_5 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=6.0, diameter_in=1.5, material="uPVC")
    hf_2_5 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=6.0, diameter_in=2.5, material="uPVC")
    assert hf_2_5 < hf_1_5

# 19. Flow effects
def test_scenario_19_flow_effects():
    hf_f5 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=5.0, diameter_in=2.0, material="uPVC")
    hf_f10 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=10.0, diameter_in=2.0, material="uPVC")
    assert hf_f10 > hf_f5

# 20. Pipe length effects
def test_scenario_20_pipe_length_effects():
    hf_l100 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=6.0, diameter_in=2.0, material="uPVC")
    hf_l200 = calculate_hazen_williams_friction(length_m=200.0, flow_m3h=6.0, diameter_in=2.0, material="uPVC")
    assert pytest.approx(hf_l200, rel=1e-5) == hf_l100 * 2.0

# 21. Unit conversion
def test_scenario_21_unit_conversion():
    assert inches_to_meters(2.0) == 0.0508
    assert m3h_to_m3s(3600.0) == 1.0

# 22. Riser pipe quantity calculation
def test_scenario_22_riser_pipe_quantity_calculation():
    assert calculate_riser_pipe_quantity(psd_m=90.0, standard_riser_length_m=3.0) == 30
    assert calculate_riser_pipe_quantity(psd_m=91.0, standard_riser_length_m=3.0) == 31

# 23. Invalid input handling
def test_scenario_23_invalid_input_handling():
    with pytest.raises(EngineeringValidationError):
        validate_borehole_inputs(yield_m3h=-5.0, pwl_m=10.0, psd_m=20.0)
    with pytest.raises(EngineeringValidationError):
        validate_borehole_inputs(yield_m3h=10.0, pwl_m=50.0, psd_m=40.0) # PSD < PWL
