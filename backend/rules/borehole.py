"""
Borehole Application Rules Engine Module.
Enforces the 80% sustainable yield rule, high-abstraction warnings, flow override rules,
PWL vs PSD distinctions, and pump depth suitability constraints.
"""

from typing import Optional, Union
from backend.rules.validation import validate_borehole_inputs
from backend.engineering.results import BoreholeCalculationResult, AbstractionStatusEnum, HydraulicResult
from backend.engineering.head import calculate_borehole_hydraulics
from backend.engineering.materials import PipeMaterial

DEFAULT_SUSTAINABLE_YIELD_FACTOR: float = 0.80
DEFAULT_HIGH_ABSTRACTION_MAX_HOURS: float = 8.0

def evaluate_borehole_application(
    yield_m3h: float,
    pwl_m: float,
    psd_m: float,
    customer_requested_flow_m3h: Optional[float] = None,
    delivery_distance_m: float = 0.0,
    destination_elevation_m: float = 0.0,
    pipe_diameter_in: Optional[float] = None,
    sustainable_yield_factor: float = DEFAULT_SUSTAINABLE_YIELD_FACTOR,
    suggested_high_abstraction_max_hours: float = DEFAULT_HIGH_ABSTRACTION_MAX_HOURS,
    riser_material: Union[str, PipeMaterial] = "uPVC",
    delivery_material: Union[str, PipeMaterial] = "HDPE",
    standard_riser_length_m: float = 3.0
) -> BoreholeCalculationResult:
    """
    Evaluate borehole rules and compute hydraulic calculation results if pipe diameter is available.
    """
    if customer_requested_flow_m3h == 0.0:
        customer_requested_flow_m3h = None

    # 1. Input Validation
    validate_borehole_inputs(
        yield_m3h=yield_m3h,
        pwl_m=pwl_m,
        psd_m=psd_m,
        customer_requested_flow_m3h=customer_requested_flow_m3h,
        delivery_distance_m=delivery_distance_m,
        destination_elevation_m=destination_elevation_m,
        pipe_diameter_in=pipe_diameter_in
    )

    # 2. Sustainable Flow Calculation
    sustainable_flow_m3h = round(yield_m3h * sustainable_yield_factor, 3)

    # 3. Customer Flow Logic & Abstraction Status
    warning_msg: Optional[str] = None
    error_msg: Optional[str] = None

    if customer_requested_flow_m3h is None:
        design_flow_m3h = sustainable_flow_m3h
        status = AbstractionStatusEnum.SUSTAINABLE
    else:
        req_flow = float(customer_requested_flow_m3h)
        design_flow_m3h = req_flow
        if req_flow >= yield_m3h:
            status = AbstractionStatusEnum.EXCEEDS_YIELD
            warning_msg = "High-abstraction operation. Not the preferred sustainable design."
        elif req_flow > sustainable_flow_m3h:
            status = AbstractionStatusEnum.HIGH_ABSTRACTION
            warning_msg = (
                f"The requested flow ({req_flow} m3/h) is above the recommended {int(sustainable_yield_factor * 100)}% "
                f"sustainable abstraction rate ({sustainable_flow_m3h} m3/h) and is close to the borehole yield ({yield_m3h} m3/h). "
                f"Suggested operating restriction: maximum {suggested_high_abstraction_max_hours} hours/day. "
                "Operating duration should be confirmed against borehole recovery/recharge characteristics and site conditions."
            )
        else:
            status = AbstractionStatusEnum.SUSTAINABLE

    # 4. Hydraulics Calculation (if pipe diameter is specified)
    hydraulic_res: Optional[HydraulicResult] = None
    if pipe_diameter_in is not None and status != AbstractionStatusEnum.EXCEEDS_YIELD:
        hydraulic_res = calculate_borehole_hydraulics(
            pwl_m=pwl_m,
            psd_m=psd_m,
            design_flow_m3h=design_flow_m3h,
            pipe_diameter_in=pipe_diameter_in,
            destination_elevation_m=destination_elevation_m,
            delivery_distance_m=delivery_distance_m,
            riser_material=riser_material,
            delivery_material=delivery_material,
            standard_riser_length_m=standard_riser_length_m
        )

    return BoreholeCalculationResult(
        application_type="borehole",
        borehole_yield_m3h=float(yield_m3h),
        sustainable_flow_m3h=sustainable_flow_m3h,
        design_flow_m3h=design_flow_m3h,
        customer_requested_flow_m3h=customer_requested_flow_m3h,
        pwl_m=float(pwl_m),
        psd_m=float(psd_m),
        destination_elevation_m=float(destination_elevation_m),
        delivery_distance_m=float(delivery_distance_m),
        abstraction_status=status,
        warning_message=warning_msg,
        error_message=error_msg,
        hydraulic_result=hydraulic_res
    )

def evaluate_pump_depth_suitability(psd_m: float, pump_max_depth_m: float) -> bool:
    """
    Hard engineering constraint: The pump setting depth (PSD) must not exceed
    the pump's maximum immersion depth rating.
    """
    if psd_m <= 0 or pump_max_depth_m <= 0:
        return False
    return psd_m <= pump_max_depth_m
