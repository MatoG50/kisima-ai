"""
Test Suite for Hazen-Williams Pipe Friction and Velocity Calculations.
"""

# pyrefly: ignore [missing-import]
import pytest
from backend.engineering.friction import calculate_hazen_williams_friction, calculate_pipe_velocity
from backend.engineering.materials import PipeMaterial, get_pipe_material

def test_hazen_williams_zero_length_or_flow():
    assert calculate_hazen_williams_friction(length_m=0.0, flow_m3h=10.0, diameter_in=2.0, material="uPVC") == 0.0
    assert calculate_hazen_williams_friction(length_m=100.0, flow_m3h=0.0, diameter_in=2.0, material="uPVC") == 0.0

def test_hazen_williams_known_numerical_value():
    # 100m uPVC (C=150) pipe, 2-inch diameter (0.0508m), flow 10 m3/h (0.00277778 m3/s)
    # Hazen-Williams exact value: 3.694 m
    hf = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=10.0, diameter_in=2.0, material="uPVC")
    assert pytest.approx(hf, rel=1e-2) == 3.69

def test_pipe_diameter_effects():
    # Larger pipe diameter must reduce friction loss (h_f proportional to D^-4.871)
    hf_1_25 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=5.0, diameter_in=1.25, material="uPVC")
    hf_2_00 = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=5.0, diameter_in=2.00, material="uPVC")
    assert hf_2_00 < hf_1_25

def test_flow_effects():
    # Higher flow rate must increase friction loss (h_f proportional to Q^1.852)
    hf_low = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=5.0, diameter_in=2.0, material="uPVC")
    hf_high = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=10.0, diameter_in=2.0, material="uPVC")
    assert hf_high > hf_low

def test_pipe_length_effects():
    # Friction loss scales linearly with pipe length (h_f proportional to L)
    hf_50m = calculate_hazen_williams_friction(length_m=50.0, flow_m3h=8.0, diameter_in=2.0, material="uPVC")
    hf_100m = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=8.0, diameter_in=2.0, material="uPVC")
    assert pytest.approx(hf_100m, rel=1e-5) == hf_50m * 2.0

def test_pipe_material_selection():
    # uPVC (C=150) should have slightly lower friction loss than HDPE (C=140)
    hf_upvc = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=8.0, diameter_in=2.0, material="uPVC")
    hf_hdpe = calculate_hazen_williams_friction(length_m=100.0, flow_m3h=8.0, diameter_in=2.0, material="HDPE")
    assert hf_upvc < hf_hdpe

def test_pipe_velocity():
    # 10 m3/h in 2-inch pipe -> v ~ 1.37 m/s
    v = calculate_pipe_velocity(flow_m3h=10.0, diameter_in=2.0)
    assert pytest.approx(v, rel=1e-2) == 1.37
