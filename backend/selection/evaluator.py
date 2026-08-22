"""
Per-Candidate Hydraulic and Duty Point Evaluator Module.
Evaluates individual candidate pumps using candidate-specific friction, TDH, curve interpolation,
and physical feasibility constraints.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum

from backend.models.pump import PumpModel, PumpCurvePoint
from backend.engineering.results import HydraulicResult
from backend.engineering.head import calculate_borehole_hydraulics
from backend.selection.interpolation import interpolate_curve_point, find_best_efficiency_point, OutOfCurveRangeError

class RejectionReasonEnum(str, Enum):
    DEPTH_EXCEEDED = "DEPTH_EXCEEDED"
    OUT_OF_CURVE_RANGE = "OUT_OF_CURVE_RANGE"
    INSUFFICIENT_HEAD = "INSUFFICIENT_HEAD"
    FAMILY_MISMATCH = "FAMILY_MISMATCH"
    INAPPROPRIATE_FLOW_CLASS = "INAPPROPRIATE_FLOW_CLASS"

def extract_nominal_flow_class(pump_id: str) -> Optional[float]:
    """
    Extracts the nominal flow class from a pump identifier.
    e.g., 'ds05-17' -> 5.0, 'dss08-11' -> 8.0, 'ds60-16' -> 60.0
    """
    first_part = pump_id.split('-')[0]
    digits = "".join(c for c in first_part if c.isdigit())
    if digits:
        return float(digits)
    return None

@dataclass
class EvaluatedCandidate:
    pump: PumpModel
    curves: List[PumpCurvePoint]
    design_flow_m3h: float
    is_depth_suitable: bool
    is_in_curve_range: bool
    is_head_suitable: bool
    is_viable: bool
    rejection_reason: Optional[RejectionReasonEnum]
    rejection_message: Optional[str]
    required_tdh_m: float
    pump_head_at_design_flow_m: float
    head_margin_m: float
    operating_efficiency_percent: float
    bep_flow_m3h: float
    bep_efficiency_percent: float
    hydraulic_result: HydraulicResult
    suitability_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pump_id": self.pump.pump_id,
            "pump_name": self.pump.pump_name,
            "motor_kw": self.pump.motor_kw,
            "max_depth_m": self.pump.max_depth_m,
            "phase_option": self.pump.phase_option.value,
            "flc_1ph_a": self.pump.flc_1ph_a,
            "flc_3ph_a": self.pump.flc_3ph_a,
            "discharge_size_in": self.pump.discharge_size_in,
            "design_flow_m3h": self.design_flow_m3h,
            "is_depth_suitable": self.is_depth_suitable,
            "is_in_curve_range": self.is_in_curve_range,
            "is_head_suitable": self.is_head_suitable,
            "is_viable": self.is_viable,
            "rejection_reason": self.rejection_reason.value if self.rejection_reason else None,
            "rejection_message": self.rejection_message,
            "required_tdh_m": self.required_tdh_m,
            "pump_head_at_design_flow_m": self.pump_head_at_design_flow_m,
            "head_margin_m": self.head_margin_m,
            "operating_efficiency_percent": self.operating_efficiency_percent,
            "bep_flow_m3h": self.bep_flow_m3h,
            "bep_efficiency_percent": self.bep_efficiency_percent,
            "suitability_score": round(self.suitability_score, 2),
            "hydraulic_result": self.hydraulic_result.to_dict() if self.hydraulic_result else None
        }

def evaluate_candidate_pump(
    pump: PumpModel,
    curves: List[PumpCurvePoint],
    pwl_m: float,
    psd_m: float,
    design_flow_m3h: float,
    delivery_distance_m: float = 0.0,
    destination_elevation_m: float = 0.0,
    riser_material: str = "uPVC",
    delivery_material: str = "HDPE"
) -> EvaluatedCandidate:
    """
    Evaluate a candidate pump against a specific duty point.
    Calculates friction and TDH using the candidate's actual discharge size.
    """
    # 1. Depth Suitability Check (Hard Constraint)
    is_depth_suitable = (psd_m <= pump.max_depth_m)

    # 2. Per-Candidate Hydraulics Calculation (using candidate discharge size)
    hydraulic_res = calculate_borehole_hydraulics(
        pwl_m=pwl_m,
        psd_m=psd_m,
        design_flow_m3h=design_flow_m3h,
        pipe_diameter_in=pump.discharge_size_in,
        destination_elevation_m=destination_elevation_m,
        delivery_distance_m=delivery_distance_m,
        riser_material=riser_material,
        delivery_material=delivery_material
    )
    required_tdh = hydraulic_res.total_dynamic_head_m

    # 3. BEP Details
    bep_point = find_best_efficiency_point(curves) if curves else None
    bep_flow = bep_point.flow_m3h if bep_point else 0.0
    bep_eta = bep_point.efficiency_percent if bep_point else 0.0

    # 4. Curve Range & Head Interpolation
    is_in_curve_range = False
    is_head_suitable = False
    pump_head_at_design_flow = 0.0
    operating_eta = 0.0
    head_margin = 0.0
    rejection_reason: Optional[RejectionReasonEnum] = None
    rejection_msg: Optional[str] = None

    if not is_depth_suitable:
        rejection_reason = RejectionReasonEnum.DEPTH_EXCEEDED
        rejection_msg = f"PSD ({psd_m} m) exceeds maximum immersion depth ({pump.max_depth_m} m)."

    try:
        interp_res = interpolate_curve_point(curves, design_flow_m3h)
        is_in_curve_range = True
        pump_head_at_design_flow = interp_res.head_m
        operating_eta = interp_res.efficiency_percent
        head_margin = round(pump_head_at_design_flow - required_tdh, 3)

        if pump_head_at_design_flow >= required_tdh:
            is_head_suitable = True
        else:
            is_head_suitable = False
            if not rejection_reason:
                rejection_reason = RejectionReasonEnum.INSUFFICIENT_HEAD
                rejection_msg = (
                    f"Pump head ({pump_head_at_design_flow} m) at design flow {design_flow_m3h} m3/h "
                    f"is less than required TDH ({required_tdh} m)."
                )
    except OutOfCurveRangeError as err:
        is_in_curve_range = False
        if not rejection_reason:
            rejection_reason = RejectionReasonEnum.OUT_OF_CURVE_RANGE
            rejection_msg = str(err)

    # 5. Appropriateness Filter
    is_flow_appropriate = True
    nominal_flow = extract_nominal_flow_class(pump.pump_id)
    if nominal_flow is not None:
        lower_bound = nominal_flow * 0.6
        upper_bound = nominal_flow * 1.4
        if not (lower_bound <= design_flow_m3h <= upper_bound):
            is_flow_appropriate = False
            if not rejection_reason:
                rejection_reason = RejectionReasonEnum.INAPPROPRIATE_FLOW_CLASS
                rejection_msg = (
                    f"Pump nominal flow class ({nominal_flow} m3/h) is not within +/- 40% margin "
                    f"of the design flow ({design_flow_m3h} m3/h)."
                )

    # 6. Overall Viability Flag
    is_viable = is_depth_suitable and is_in_curve_range and is_head_suitable and is_flow_appropriate

    return EvaluatedCandidate(
        pump=pump,
        curves=curves,
        design_flow_m3h=design_flow_m3h,
        is_depth_suitable=is_depth_suitable,
        is_in_curve_range=is_in_curve_range,
        is_head_suitable=is_head_suitable,
        is_viable=is_viable,
        rejection_reason=rejection_reason,
        rejection_message=rejection_msg,
        required_tdh_m=required_tdh,
        pump_head_at_design_flow_m=pump_head_at_design_flow,
        head_margin_m=head_margin,
        operating_efficiency_percent=operating_eta,
        bep_flow_m3h=bep_flow,
        bep_efficiency_percent=bep_eta,
        hydraulic_result=hydraulic_res,
        suitability_score=0.0
    )
