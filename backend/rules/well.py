"""
Well Application Rules Engine Module.
Implements the 3.0 m3/h default design flow rule, DSD pump family selection baseline,
customer flow override logic, and modular well hydraulics calculations.
"""

from typing import Optional, Union
from backend.rules.validation import validate_well_inputs
from backend.engineering.results import WellCalculationResult, HydraulicResult
from backend.engineering.friction import calculate_hazen_williams_friction, calculate_pipe_velocity
from backend.engineering.materials import PipeMaterial, get_pipe_material

DEFAULT_WELL_DESIGN_FLOW_M3H: float = 3.0
DEFAULT_WELL_PUMP_FAMILY: str = "DSD"

def evaluate_well_application(
    static_head_m: float,
    customer_requested_flow_m3h: Optional[float] = None,
    delivery_distance_m: float = 0.0,
    pipe_diameter_in: Optional[float] = None,
    default_design_flow_m3h: float = DEFAULT_WELL_DESIGN_FLOW_M3H,
    default_pump_family: str = DEFAULT_WELL_PUMP_FAMILY,
    delivery_material: Union[str, PipeMaterial] = "HDPE"
) -> WellCalculationResult:
    """
    Evaluate well application rules and compute hydraulics.
    """
    # 1. Validation
    validate_well_inputs(
        static_head_m=static_head_m,
        customer_requested_flow_m3h=customer_requested_flow_m3h,
        delivery_distance_m=delivery_distance_m,
        pipe_diameter_in=pipe_diameter_in
    )

    # 2. Design Flow Logic
    if customer_requested_flow_m3h is None:
        design_flow_m3h = default_design_flow_m3h
        is_default_used = True
    else:
        design_flow_m3h = float(customer_requested_flow_m3h)
        is_default_used = False

    # 3. Hydraulics (if pipe diameter supplied)
    hydraulic_res: Optional[HydraulicResult] = None
    if pipe_diameter_in is not None:
        delivery_mat_obj = get_pipe_material(delivery_material) if isinstance(delivery_material, str) else delivery_material
        delivery_friction = calculate_hazen_williams_friction(
            length_m=delivery_distance_m,
            flow_m3h=design_flow_m3h,
            diameter_in=pipe_diameter_in,
            material=delivery_mat_obj
        )
        tdh_m = static_head_m + delivery_friction
        velocity = calculate_pipe_velocity(design_flow_m3h, pipe_diameter_in)

        hydraulic_res = HydraulicResult(
            static_head_m=round(static_head_m, 3),
            riser_length_m=0.0,
            riser_friction_m=0.0,
            delivery_length_m=round(delivery_distance_m, 3),
            delivery_friction_m=round(delivery_friction, 3),
            total_dynamic_head_m=round(tdh_m, 3),
            riser_pipe_quantity=0,
            standard_riser_length_m=3.0,
            riser_material="N/A",
            delivery_material=delivery_mat_obj.name,
            pipe_diameter_in=pipe_diameter_in,
            velocity_m_s=round(velocity, 3)
        )

    return WellCalculationResult(
        application_type="well",
        design_flow_m3h=design_flow_m3h,
        customer_requested_flow_m3h=customer_requested_flow_m3h,
        is_default_flow_used=is_default_used,
        default_pump_family=default_pump_family,
        static_head_m=float(static_head_m),
        delivery_distance_m=float(delivery_distance_m),
        hydraulic_result=hydraulic_res
    )
