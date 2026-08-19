from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, model_validator, Field

class RecommendationRequestSchema(BaseModel):
    application_type: Literal["borehole", "well"] = Field(..., description="Installation mode: 'borehole' or 'well'")
    
    # Borehole specific fields
    yield_m3h: Optional[float] = Field(None, description="Borehole yield in m3/h (Required for borehole)")
    pwl_m: Optional[float] = Field(None, description="Pumping Water Level in meters (Required for borehole)")
    psd_m: Optional[float] = Field(None, description="Pump Setting Depth in meters (Required for borehole)")
    
    # Well specific fields
    static_head_m: Optional[float] = Field(None, description="Static head in meters (Required for well)")
    
    # Optional common fields
    customer_requested_flow_m3h: Optional[float] = Field(None, description="Optional customer requested flow in m3/h")
    delivery_distance_m: float = Field(0.0, ge=0.0, description="Delivery pipe length in meters")
    destination_elevation_m: float = Field(0.0, ge=0.0, description="Destination elevation above ground in meters")
    default_pump_family: str = Field("DSD", description="Default candidate family for well sizing")

    @model_validator(mode="after")
    def validate_application_inputs(self):
        app_type = self.application_type.lower()
        
        if app_type == "borehole":
            if self.yield_m3h is None or self.yield_m3h <= 0:
                raise ValueError("Borehole application requires a positive 'yield_m3h' (> 0).")
            if self.pwl_m is None or self.pwl_m < 0:
                raise ValueError("Borehole application requires a non-negative 'pwl_m' (>= 0).")
            if self.psd_m is None or self.psd_m <= 0:
                raise ValueError("Borehole application requires a positive 'psd_m' (> 0).")
            if self.psd_m < self.pwl_m:
                raise ValueError(f"Pump Setting Depth (psd_m={self.psd_m}m) cannot be shallower than Pumping Water Level (pwl_m={self.pwl_m}m).")
        elif app_type == "well":
            if self.static_head_m is None or self.static_head_m < 0:
                raise ValueError("Well application requires a non-negative 'static_head_m' (>= 0).")

        if self.customer_requested_flow_m3h is not None and self.customer_requested_flow_m3h <= 0:
            raise ValueError("Customer requested flow must be strictly positive (> 0 m3/h).")

        return self

class HydraulicResultSchema(BaseModel):
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

class RecommendedPumpSchema(BaseModel):
    pump_id: str
    pump_name: str
    motor_kw: float
    max_depth_m: float
    phase_option: str
    flc_1ph_a: Optional[float] = None
    flc_3ph_a: Optional[float] = None
    discharge_size_in: float
    design_flow_m3h: float
    is_depth_suitable: bool
    is_in_curve_range: bool
    is_head_suitable: bool
    is_viable: bool
    required_tdh_m: float
    pump_head_at_design_flow_m: float
    head_margin_m: float
    operating_efficiency_percent: float
    bep_flow_m3h: float
    bep_efficiency_percent: float
    suitability_score: float
    hydraulic_result: Optional[HydraulicResultSchema] = None

class RejectionSummarySchema(BaseModel):
    total_candidates_evaluated: int
    viable_candidates_count: int
    rejected_depth_exceeded: int = 0
    rejected_out_of_range: int = 0
    rejected_insufficient_head: int = 0
    reason: Optional[str] = None

class RecommendationResponseSchema(BaseModel):
    status: str
    application_type: str
    design_flow_m3h: Optional[float] = None
    abstraction_status: Optional[str] = None
    yield_m3h: Optional[float] = None
    pwl_m: Optional[float] = None
    psd_m: Optional[float] = None
    static_head_m: Optional[float] = None
    destination_elevation_m: Optional[float] = None
    delivery_distance_m: Optional[float] = None
    warnings: List[str] = []
    error_message: Optional[str] = None
    recommended_pump: Optional[RecommendedPumpSchema] = None
    alternatives: List[RecommendedPumpSchema] = []
    rejection_summary: Optional[RejectionSummarySchema] = None
