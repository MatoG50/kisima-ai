"""
Input Validation and Physical Feasibility Rules Module.
Rejects physically impossible inputs and raises descriptive ValidationErrors.
"""

from typing import Optional

class EngineeringValidationError(ValueError):
    """Exception raised when engineering input parameters fail validation."""
    pass

def validate_borehole_inputs(
    yield_m3h: float,
    pwl_m: float,
    psd_m: float,
    customer_requested_flow_m3h: Optional[float] = None,
    delivery_distance_m: float = 0.0,
    destination_elevation_m: float = 0.0,
    pipe_diameter_in: Optional[float] = None
) -> None:
    """
    Validate borehole input parameters. Raises EngineeringValidationError if invalid.
    """
    if yield_m3h <= 0:
        raise EngineeringValidationError(f"Borehole yield must be strictly positive (> 0 m3/h), got {yield_m3h}")
    if pwl_m < 0:
        raise EngineeringValidationError(f"Pumping Water Level (PWL) cannot be negative, got {pwl_m} m")
    if psd_m <= 0:
        raise EngineeringValidationError(f"Pump Setting Depth (PSD) must be strictly positive (> 0 m), got {psd_m} m")
    if psd_m < pwl_m:
        raise EngineeringValidationError(
            f"Pump Setting Depth (PSD={psd_m}m) cannot be shallower than Pumping Water Level (PWL={pwl_m}m). "
            "The pump must be installed below the water level."
        )
    if customer_requested_flow_m3h is not None and customer_requested_flow_m3h <= 0:
        raise EngineeringValidationError(f"Requested customer flow must be strictly positive (> 0 m3/h), got {customer_requested_flow_m3h}")
    if delivery_distance_m < 0:
        raise EngineeringValidationError(f"Delivery distance cannot be negative, got {delivery_distance_m} m")
    if destination_elevation_m < 0:
        raise EngineeringValidationError(f"Destination elevation cannot be negative, got {destination_elevation_m} m")
    if pipe_diameter_in is not None and pipe_diameter_in <= 0:
        raise EngineeringValidationError(f"Pipe diameter must be positive, got {pipe_diameter_in} in")

def validate_well_inputs(
    static_head_m: float,
    customer_requested_flow_m3h: Optional[float] = None,
    delivery_distance_m: float = 0.0,
    pipe_diameter_in: Optional[float] = None
) -> None:
    """
    Validate well input parameters. Raises EngineeringValidationError if invalid.
    """
    if static_head_m < 0:
        raise EngineeringValidationError(f"Well static head cannot be negative, got {static_head_m} m")
    if customer_requested_flow_m3h is not None and customer_requested_flow_m3h <= 0:
        raise EngineeringValidationError(f"Requested customer flow must be strictly positive (> 0 m3/h), got {customer_requested_flow_m3h}")
    if delivery_distance_m < 0:
        raise EngineeringValidationError(f"Delivery distance cannot be negative, got {delivery_distance_m} m")
    if pipe_diameter_in is not None and pipe_diameter_in <= 0:
        raise EngineeringValidationError(f"Pipe diameter must be positive, got {pipe_diameter_in} in")
