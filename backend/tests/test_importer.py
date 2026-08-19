# pyrefly: ignore [missing-import]
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.models.pump import PumpModel, PumpCurvePoint, PhaseOptionEnum
from backend.validation.validator import PumpValidator

def test_phase_option_enum_parsing():
    assert PhaseOptionEnum.from_raw_string('1') == PhaseOptionEnum.PHASE_1
    assert PhaseOptionEnum.from_raw_string('1PH') == PhaseOptionEnum.PHASE_1
    assert PhaseOptionEnum.from_raw_string('3') == PhaseOptionEnum.PHASE_3
    assert PhaseOptionEnum.from_raw_string('3PH') == PhaseOptionEnum.PHASE_3
    assert PhaseOptionEnum.from_raw_string('1,3') == PhaseOptionEnum.PHASE_1_3
    assert PhaseOptionEnum.from_raw_string('1, 3') == PhaseOptionEnum.PHASE_1_3
    assert PhaseOptionEnum.from_raw_string('invalid') is None
    assert PhaseOptionEnum.from_raw_string(None) is None

def test_valid_dataset_validation():
    raw_pumps = [
        {
            'pump_id': 'ds02-09',
            'pump_name': 'dayliff ds2/9',
            'motor_kw': '0.37',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '9',
            'FLC_3x415V_A': None,
            'pipe_size': '1.25'
        },
        {
            'pump_id': 'ds02-23',
            'pump_name': 'dayliff ds2/23',
            'motor_kw': '1.1',
            'max_depth': '200',
            'phase_option': '1,3',
            'FLC_1x240V_A': '32',
            'FLC_3x415V_A': '16',
            'pipe_size': '1.25'
        }
    ]
    raw_curves = [
        {'pump_id': 'DS02-09', 'flow': '0', 'head': '51.3', 'eta': '1.2'},
        {'pump_id': 'ds02-09', 'flow': '0.5', 'head': '51.3', 'eta': '23.7'},
        {'pump_id': 'ds02-23', 'flow': '0', 'head': '130.0', 'eta': '1.5'},
        {'pump_id': 'ds02-23', 'flow': '4.0', 'head': '110.0', 'eta': '45.0'}
    ]

    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is True
    assert len(res.valid_pumps) == 2
    assert len(res.valid_curves) == 4
    # Verify ID normalization to lower case
    assert res.valid_pumps[0].pump_id == 'ds02-09'
    assert res.valid_curves[0].pump_id == 'ds02-09'
    # Verify raw ID preservation
    assert res.valid_pumps[0].raw_pump_id == 'ds02-09'

def test_invalid_data_bounds():
    raw_pumps = [
        {
            'pump_id': 'bad-01',
            'pump_name': 'Bad Pump',
            'motor_kw': '-1.0',  # Negative motor kw
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        }
    ]
    raw_curves = []
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is False
    assert any('motor_kw' in e for e in res.errors)

def test_efficiency_out_of_bounds():
    raw_pumps = [
        {
            'pump_id': 'pump-01',
            'pump_name': 'Pump 01',
            'motor_kw': '1.0',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        }
    ]
    raw_curves = [
        {'pump_id': 'pump-01', 'flow': '1.0', 'head': '50.0', 'eta': '150.0'} # > 100%
    ]
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is False
    assert any('Efficiency out of range' in e for e in res.errors)

def test_duplicate_pump_ids():
    raw_pumps = [
        {
            'pump_id': 'dup-01',
            'pump_name': 'Pump A',
            'motor_kw': '1.0',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        },
        {
            'pump_id': 'DUP-01', # Same ID different case
            'pump_name': 'Pump B',
            'motor_kw': '1.0',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        }
    ]
    raw_curves = []
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is False
    assert any('Duplicate pump_id' in e for e in res.errors)

def test_duplicate_curve_flow_points():
    raw_pumps = [
        {
            'pump_id': 'pump-01',
            'pump_name': 'Pump 01',
            'motor_kw': '1.0',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        }
    ]
    raw_curves = [
        {'pump_id': 'pump-01', 'flow': '1.0', 'head': '50.0', 'eta': '40.0'},
        {'pump_id': 'pump-01', 'flow': '1.0', 'head': '48.0', 'eta': '42.0'} # duplicate flow 1.0
    ]
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is False
    assert any('Duplicate curve point at flow=1.0' in e for e in res.errors)

def test_orphan_curve_points():
    raw_pumps = []
    raw_curves = [
        {'pump_id': 'unknown-pump', 'flow': '1.0', 'head': '50.0', 'eta': '40.0'}
    ]
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is False
    assert any('Orphan curve point' in e for e in res.errors)

def test_preservation_of_non_uniform_flow_points():
    raw_pumps = [
        {
            'pump_id': 'pump-a',
            'pump_name': 'Pump A',
            'motor_kw': '1.0',
            'max_depth': '200',
            'phase_option': '1',
            'FLC_1x240V_A': '5',
            'pipe_size': '1.25'
        },
        {
            'pump_id': 'pump-b',
            'pump_name': 'Pump B',
            'motor_kw': '5.0',
            'max_depth': '200',
            'phase_option': '3',
            'FLC_3x415V_A': '10',
            'pipe_size': '2.0'
        }
    ]
    # Pump A: flow step 0.5; Pump B: flow step 4.0
    raw_curves = [
        {'pump_id': 'pump-a', 'flow': '0', 'head': '50', 'eta': '1'},
        {'pump_id': 'pump-a', 'flow': '0.5', 'head': '48', 'eta': '25'},
        {'pump_id': 'pump-a', 'flow': '1.0', 'head': '45', 'eta': '40'},
        {'pump_id': 'pump-b', 'flow': '0', 'head': '100', 'eta': '2'},
        {'pump_id': 'pump-b', 'flow': '4.0', 'head': '95', 'eta': '30'},
        {'pump_id': 'pump-b', 'flow': '8.0', 'head': '85', 'eta': '55'}
    ]
    res = PumpValidator.validate_dataset(raw_pumps, raw_curves)
    assert res.is_valid is True
    
    pump_a_flows = [c.flow_m3h for c in res.valid_curves if c.pump_id == 'pump-a']
    pump_b_flows = [c.flow_m3h for c in res.valid_curves if c.pump_id == 'pump-b']
    
    assert pump_a_flows == [0.0, 0.5, 1.0]
    assert pump_b_flows == [0.0, 4.0, 8.0]
