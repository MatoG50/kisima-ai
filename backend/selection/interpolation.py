"""
Performance Curve Linear Interpolation Module.
Evaluates pump head and efficiency at an arbitrary design flow Q using linear interpolation.
Extrapolation outside curve bounds is prohibited.
"""

from dataclasses import dataclass
from typing import List, Optional
from backend.models.pump import PumpCurvePoint

class OutOfCurveRangeError(ValueError):
    """Exception raised when design flow lies outside the pump's curve range."""
    pass

@dataclass
class InterpolatedPoint:
    flow_m3h: float
    head_m: float
    efficiency_percent: float
    is_exact_match: bool

def interpolate_curve_point(curves: List[PumpCurvePoint], target_flow_m3h: float) -> InterpolatedPoint:
    """
    Interpolate head (m) and efficiency (%) at target_flow_m3h using linear interpolation
    between surrounding flow points.
    
    Raises:
    - ValueError if curves list is empty.
    - OutOfCurveRangeError if target_flow_m3h < min_flow or target_flow_m3h > max_flow.
    """
    if not curves:
        raise ValueError("Cannot interpolate on empty curve points list.")
        
    # Ensure curve points are sorted by flow ascending
    sorted_curves = sorted(curves, key=lambda c: c.flow_m3h)
    
    q_min = sorted_curves[0].flow_m3h
    q_max = sorted_curves[-1].flow_m3h
    
    # Boundary check (no extrapolation)
    if target_flow_m3h < q_min:
        raise OutOfCurveRangeError(
            f"Target flow {target_flow_m3h} m3/h is below minimum pump curve flow {q_min} m3/h."
        )
    if target_flow_m3h > q_max:
        raise OutOfCurveRangeError(
            f"Target flow {target_flow_m3h} m3/h exceeds maximum pump curve flow {q_max} m3/h."
        )

    # 1. Exact match check
    for p in sorted_curves:
        if abs(p.flow_m3h - target_flow_m3h) < 1e-6:
            return InterpolatedPoint(
                flow_m3h=target_flow_m3h,
                head_m=p.head_m,
                efficiency_percent=p.efficiency_percent,
                is_exact_match=True
            )

    # 2. Linear interpolation between surrounding points
    for i in range(len(sorted_curves) - 1):
        p1 = sorted_curves[i]
        p2 = sorted_curves[i+1]
        
        if p1.flow_m3h < target_flow_m3h < p2.flow_m3h:
            delta_q = p2.flow_m3h - p1.flow_m3h
            if delta_q == 0:
                continue
                
            t = (target_flow_m3h - p1.flow_m3h) / delta_q
            head_interp = p1.head_m + t * (p2.head_m - p1.head_m)
            eta_interp = p1.efficiency_percent + t * (p2.efficiency_percent - p1.efficiency_percent)
            
            return InterpolatedPoint(
                flow_m3h=target_flow_m3h,
                head_m=round(head_interp, 3),
                efficiency_percent=round(eta_interp, 3),
                is_exact_match=False
            )

    # Fallback safety check (should not be reached)
    raise OutOfCurveRangeError(f"Flow {target_flow_m3h} m3/h could not be interpolated on curve.")

def find_best_efficiency_point(curves: List[PumpCurvePoint]) -> PumpCurvePoint:
    """Return the curve point with the maximum efficiency (BEP)."""
    if not curves:
        raise ValueError("Cannot find BEP on empty curve list.")
    return max(curves, key=lambda c: c.efficiency_percent)
