"""
Structured Engineering Result Objects Module.
Provides dataclasses and serialization methods for hydraulic and business rule results.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from enum import Enum

class AbstractionStatusEnum(str, Enum):
    SUSTAINABLE = "SUSTAINABLE"
    HIGH_ABSTRACTION = "HIGH_ABSTRACTION"
    EXCEEDS_YIELD = "EXCEEDS_YIELD"

@dataclass
class HydraulicResult:
    static_head_m: float
    riser_length_m: float
    riser_friction_m: float
    delivery_length_m: float
    delivery_friction_m: float
    total_dynamic_head_m: float
    riser_pipe_quantity: int
    standard_riser_length_m: float
    riser_material: str
    delivery_material: str
    pipe_diameter_in: float
    velocity_m_s: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BoreholeCalculationResult:
    application_type: str = "borehole"
    borehole_yield_m3h: float = 0.0
    sustainable_flow_m3h: float = 0.0
    design_flow_m3h: float = 0.0
    customer_requested_flow_m3h: Optional[float] = None
    pwl_m: float = 0.0
    psd_m: float = 0.0
    destination_elevation_m: float = 0.0
    delivery_distance_m: float = 0.0
    abstraction_status: AbstractionStatusEnum = AbstractionStatusEnum.SUSTAINABLE
    warning_message: Optional[str] = None
    error_message: Optional[str] = None
    hydraulic_result: Optional[HydraulicResult] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["abstraction_status"] = self.abstraction_status.value
        return d

@dataclass
class WellCalculationResult:
    application_type: str = "well"
    design_flow_m3h: float = 3.0
    customer_requested_flow_m3h: Optional[float] = None
    is_default_flow_used: bool = True
    default_pump_family: str = "DSD"
    static_head_m: float = 0.0
    delivery_distance_m: float = 0.0
    warning_message: Optional[str] = None
    error_message: Optional[str] = None
    hydraulic_result: Optional[HydraulicResult] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
