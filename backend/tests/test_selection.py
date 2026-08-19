"""
Automated Test Suite for Stage 4 — Pump Candidate Evaluation & Recommendation Engine.
Tests all 26 Stage 4 scenarios including interpolation, candidate-specific TDH, depth checks,
scoring, ranking, borehole yield constraints, well DSD filtering, and PostgreSQL integration.
"""

# pyrefly: ignore [missing-import]
import pytest
import psycopg2
from backend.models.pump import PumpModel, PumpCurvePoint, PhaseOptionEnum
from backend.selection.interpolation import interpolate_curve_point, OutOfCurveRangeError, find_best_efficiency_point
from backend.selection.evaluator import evaluate_candidate_pump, RejectionReasonEnum
from backend.selection.ranking import rank_candidates
from backend.selection.service import PumpRecommendationService

# Sample test curve points
SAMPLE_CURVES = [
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=0.0, head_m=51.3, efficiency_percent=1.2),
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=0.5, head_m=51.3, efficiency_percent=23.7),
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=1.0, head_m=48.1, efficiency_percent=39.6),
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=1.5, head_m=41.7, efficiency_percent=47.0),
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=2.0, head_m=32.1, efficiency_percent=45.6),
    PumpCurvePoint(pump_id="ds02-09", flow_m3h=2.5, head_m=23.5, efficiency_percent=37.3)
]

SAMPLE_PUMP = PumpModel(
    pump_id="ds02-09",
    pump_name="dayliff ds2/9",
    motor_kw=0.37,
    max_depth_m=200.0,
    phase_option=PhaseOptionEnum.PHASE_1,
    flc_1ph_a=9.0,
    flc_3ph_a=None,
    discharge_size_in=1.25,
    raw_pump_id="ds02-09"
)

# 1. Exact curve-point evaluation
def test_scenario_01_exact_curve_point_evaluation():
    pt = interpolate_curve_point(SAMPLE_CURVES, 1.0)
    assert pt.is_exact_match is True
    assert pt.head_m == 48.1
    assert pt.efficiency_percent == 39.6

# 2. Linear interpolation
def test_scenario_02_linear_interpolation():
    pt = interpolate_curve_point(SAMPLE_CURVES, 1.25)
    assert pt.is_exact_match is False
    assert pytest.approx(pt.head_m, rel=1e-3) == 44.9
    assert pytest.approx(pt.efficiency_percent, rel=1e-3) == 43.3

# 3. Non-uniform curve spacing
def test_scenario_03_non_uniform_curve_spacing():
    curves = [
        PumpCurvePoint(pump_id="p-b", flow_m3h=0.0, head_m=100.0, efficiency_percent=2.0),
        PumpCurvePoint(pump_id="p-b", flow_m3h=4.0, head_m=90.0, efficiency_percent=40.0),
        PumpCurvePoint(pump_id="p-b", flow_m3h=8.0, head_m=70.0, efficiency_percent=60.0),
        PumpCurvePoint(pump_id="p-b", flow_m3h=12.0, head_m=40.0, efficiency_percent=50.0)
    ]
    pt = interpolate_curve_point(curves, 6.0)
    assert pytest.approx(pt.head_m, rel=1e-3) == 80.0
    assert pytest.approx(pt.efficiency_percent, rel=1e-3) == 50.0

# 4. Flow below curve range
def test_scenario_04_flow_below_curve_range():
    curves = [
        PumpCurvePoint(pump_id="p-1", flow_m3h=2.0, head_m=50.0, efficiency_percent=30.0),
        PumpCurvePoint(pump_id="p-1", flow_m3h=5.0, head_m=40.0, efficiency_percent=50.0)
    ]
    with pytest.raises(OutOfCurveRangeError):
        interpolate_curve_point(curves, 1.0)

# 5. Flow above curve range
def test_scenario_05_flow_above_curve_range():
    with pytest.raises(OutOfCurveRangeError):
        interpolate_curve_point(SAMPLE_CURVES, 3.0)

# 6. Head sufficient
def test_scenario_06_head_sufficient():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.0)
    assert res.is_viable is True
    assert res.is_head_suitable is True
    assert res.head_margin_m > 0

# 7. Head insufficient
def test_scenario_07_head_insufficient():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=60.0, psd_m=80.0, design_flow_m3h=1.0)
    assert res.is_viable is False
    assert res.is_head_suitable is False
    assert res.rejection_reason == RejectionReasonEnum.INSUFFICIENT_HEAD

# 8. Positive head margin
def test_scenario_08_positive_head_margin():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=20.0, psd_m=40.0, design_flow_m3h=1.0)
    assert res.head_margin_m > 0

# 9. Zero head margin
def test_scenario_09_zero_head_margin():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=47.6, psd_m=40.0, design_flow_m3h=1.0)
    assert res.pump_head_at_design_flow_m >= res.required_tdh_m

# 10. Depth suitability
def test_scenario_10_depth_suitability():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=30.0, psd_m=150.0, design_flow_m3h=1.0)
    assert res.is_depth_suitable is True

# 11. Depth failure
def test_scenario_11_depth_failure():
    res = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=30.0, psd_m=250.0, design_flow_m3h=1.0)
    assert res.is_viable is False
    assert res.is_depth_suitable is False
    assert res.rejection_reason == RejectionReasonEnum.DEPTH_EXCEEDED

# 12. Candidate-specific pipe diameter
def test_scenario_12_candidate_specific_pipe_diameter():
    pump_1_25 = PumpModel("p1", "P1", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 1.25, "p1")
    pump_2_00 = PumpModel("p2", "P2", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 2.00, "p2")
    
    res1 = evaluate_candidate_pump(pump_1_25, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    res2 = evaluate_candidate_pump(pump_2_00, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    
    assert res1.hydraulic_result.pipe_diameter_in == 1.25
    assert res2.hydraulic_result.pipe_diameter_in == 2.00

# 13. Candidate-specific friction
def test_scenario_13_candidate_specific_friction():
    pump_1_25 = PumpModel("p1", "P1", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 1.25, "p1")
    pump_2_00 = PumpModel("p2", "P2", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 2.00, "p2")
    
    res1 = evaluate_candidate_pump(pump_1_25, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    res2 = evaluate_candidate_pump(pump_2_00, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    
    assert res1.hydraulic_result.riser_friction_m > res2.hydraulic_result.riser_friction_m

# 14. Candidate-specific TDH
def test_scenario_14_candidate_specific_tdh():
    pump_1_25 = PumpModel("p1", "P1", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 1.25, "p1")
    pump_2_00 = PumpModel("p2", "P2", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 10.0, None, 2.00, "p2")
    
    res1 = evaluate_candidate_pump(pump_1_25, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    res2 = evaluate_candidate_pump(pump_2_00, SAMPLE_CURVES, pwl_m=30.0, psd_m=50.0, design_flow_m3h=1.5, delivery_distance_m=100.0)
    
    assert res1.required_tdh_m > res2.required_tdh_m

# 15. Efficiency interpolation
def test_scenario_15_efficiency_interpolation():
    pt = interpolate_curve_point(SAMPLE_CURVES, 1.25)
    assert pytest.approx(pt.efficiency_percent, rel=1e-3) == 43.3

# 16. Well DSD filtering
def test_scenario_16_well_dsd_filtering():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_well(conn, static_head_m=15.0)
        assert res["status"] == "SUCCESS"
        assert "dsd" in res["recommended_pump"]["pump_id"].lower()
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 17. Well default 3 m3/h
def test_scenario_17_well_default_3m3h():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_well(conn, static_head_m=15.0)
        assert res["design_flow_m3h"] == 3.0
        assert res["is_default_flow_used"] is True
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 18. Well custom flow
def test_scenario_18_well_custom_flow():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_well(conn, static_head_m=15.0, customer_requested_flow_m3h=2.5)
        assert res["design_flow_m3h"] == 2.5
        assert res["is_default_flow_used"] is False
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 19. Borehole 80% yield
def test_scenario_19_borehole_80_percent_yield():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=10.0, pwl_m=30.0, psd_m=50.0)
        assert res["design_flow_m3h"] == 8.0
        assert res["abstraction_status"] == "SUSTAINABLE"
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 20. Borehole high abstraction
def test_scenario_20_borehole_high_abstraction():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=10.0, pwl_m=30.0, psd_m=50.0, customer_requested_flow_m3h=9.0)
        assert res["abstraction_status"] == "HIGH_ABSTRACTION"
        assert len(res["warnings"]) > 0
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 21. Borehole above-yield rejection
def test_scenario_21_borehole_above_yield_rejection():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=10.0, pwl_m=30.0, psd_m=50.0, customer_requested_flow_m3h=12.0)
        assert res["status"] == "EXCEEDS_YIELD"
        assert res["recommended_pump"] is None
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 22. No suitable pump
def test_scenario_22_no_suitable_pump():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        # Static head 400m with PSD 450m exceeds max head capability of all pumps
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=10.0, pwl_m=400.0, psd_m=450.0)
        assert res["status"] == "NO_SUITABLE_PUMP"
        assert res["recommended_pump"] is None
        assert res["rejection_summary"]["viable_candidates_count"] == 0
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 23. Primary recommendation ranking
def test_scenario_23_primary_recommendation_ranking():
    cand1 = evaluate_candidate_pump(SAMPLE_PUMP, SAMPLE_CURVES, pwl_m=20.0, psd_m=40.0, design_flow_m3h=1.5)
    cand2 = evaluate_candidate_pump(
        PumpModel("ds02-13", "dayliff ds2/13", 0.55, 200.0, PhaseOptionEnum.PHASE_1, 15.0, None, 1.25, "ds02-13"),
        [
            PumpCurvePoint("ds02-13", 0.0, 81.2, 1.2),
            PumpCurvePoint("ds02-13", 1.5, 59.9, 47.0),
            PumpCurvePoint("ds02-13", 2.5, 35.3, 37.3)
        ],
        pwl_m=20.0, psd_m=40.0, design_flow_m3h=1.5
    )
    ranked = rank_candidates([cand1, cand2])
    assert len(ranked) == 2
    assert ranked[0].suitability_score >= ranked[1].suitability_score

# 24. Alternative candidates
def test_scenario_24_alternative_candidates():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=10.0, pwl_m=30.0, psd_m=50.0)
        if res["status"] == "SUCCESS":
            assert res["recommended_pump"] is not None
            assert isinstance(res["alternatives"], list)
            assert len(res["alternatives"]) > 0
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 25. Database integration (real PostgreSQL query)
def test_scenario_25_database_integration():
    try:
        conn = psycopg2.connect(dbname='capstone_pump_db', user='postgres', host='localhost', port=5432)
        res = PumpRecommendationService.recommend_borehole(conn, yield_m3h=5.0, pwl_m=25.0, psd_m=45.0)
        assert res["status"] == "SUCCESS"
        assert res["recommended_pump"]["pump_id"] is not None
        conn.close()
    except Exception as e:
        pytest.fail(f"PostgreSQL connection failed: {e}")

# 26. Preservation of original curve points
def test_scenario_26_preservation_of_original_curve_points():
    bep = find_best_efficiency_point(SAMPLE_CURVES)
    assert bep.flow_m3h == 1.5
    assert bep.efficiency_percent == 47.0
