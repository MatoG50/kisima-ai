"""
Head Calculation and Hydraulic Loss Module.
Calculates static head, riser pipe quantity, friction losses, and Total Dynamic Head (TDH).
"""

import math
from typing import Optional, Union
from backend.engineering.friction import calculate_hazen_williams_friction, calculate_pipe_velocity
from backend.engineering.materials import PipeMaterial, get_pipe_material
from backend.engineering.results import HydraulicResult

# Configurable standard riser pipe length default (meters)
DEFAULT_STANDARD_RISER_LENGTH_M: float = 3.0

def calculate_static_head(pwl_m: float, destination_elevation_m: float = 0.0) -> float:
    """
    Calculate static head for a borehole:
        static_head = PWL + destination_elevation
    
    IMPORTANT: PWL determines static head. PSD is strictly NOT used in static head.
    """
    if pwl_m < 0:
        raise ValueError(f"Pumping Water Level (PWL) cannot be negative, got {pwl_m} m")
    if destination_elevation_m < 0:
        raise ValueError(f"Destination elevation cannot be negative, got {destination_elevation_m} m")
    return float(pwl_m + destination_elevation_m)

def calculate_riser_pipe_quantity(psd_m: float, standard_riser_length_m: float = DEFAULT_STANDARD_RISER_LENGTH_M) -> int:
    """
    Calculate the required number of individual riser pipe lengths:
        count = ceil(PSD / standard_riser_length)
    """
    if psd_m <= 0:
        raise ValueError(f"Pump Setting Depth (PSD) must be positive, got {psd_m} m")
    if standard_riser_length_m <= 0:
        raise ValueError(f"Standard riser pipe length must be positive, got {standard_riser_length_m} m")
    return int(math.ceil(psd_m / standard_riser_length_m))

def calculate_borehole_hydraulics(
    pwl_m: float,
    psd_m: float,
    design_flow_m3h: float,
    pipe_diameter_in: float,
    destination_elevation_m: float = 0.0,
    delivery_distance_m: float = 0.0,
    riser_material: Union[str, PipeMaterial] = "uPVC",
    delivery_material: Union[str, PipeMaterial] = "HDPE",
    standard_riser_length_m: float = DEFAULT_STANDARD_RISER_LENGTH_M
) -> HydraulicResult:
    """
    Calculate full hydraulic results (static head, riser friction, delivery friction, TDH, riser pipe quantity).
    """
    static_head = calculate_static_head(pwl_m, destination_elevation_m)
    riser_quantity = calculate_riser_pipe_quantity(psd_m, standard_riser_length_m)

    # Riser pipe friction loss (length approx equal to PSD)
    riser_mat_obj = get_pipe_material(riser_material) if isinstance(riser_material, str) else riser_material
    riser_friction = calculate_hazen_williams_friction(
        length_m=psd_m,
        flow_m3h=design_flow_m3h,
        diameter_in=pipe_diameter_in,
        material=riser_mat_obj
    )

    # Delivery pipe friction loss (length equal to delivery distance)
    delivery_mat_obj = get_pipe_material(delivery_material) if isinstance(delivery_material, str) else delivery_material
    delivery_friction = calculate_hazen_williams_friction(
        length_m=delivery_distance_m,
        flow_m3h=design_flow_m3h,
        diameter_in=pipe_diameter_in,
        material=delivery_mat_obj
    )

    # Total Dynamic Head (TDH) = static_head + riser_friction + delivery_friction
    tdh_m = static_head + riser_friction + delivery_friction
    velocity = calculate_pipe_velocity(design_flow_m3h, pipe_diameter_in)

    return HydraulicResult(
        static_head_m=round(static_head, 3),
        riser_length_m=round(psd_m, 3),
        riser_friction_m=round(riser_friction, 3),
        delivery_length_m=round(delivery_distance_m, 3),
        delivery_friction_m=round(delivery_friction, 3),
        total_dynamic_head_m=round(tdh_m, 3),
        riser_pipe_quantity=riser_quantity,
        standard_riser_length_m=standard_riser_length_m,
        riser_material=riser_mat_obj.name,
        delivery_material=delivery_mat_obj.name,
        pipe_diameter_in=pipe_diameter_in,
        velocity_m_s=round(velocity, 3)
    )
