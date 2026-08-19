from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class CurvePointSchema(BaseModel):
    flow_m3h: float
    head_m: float
    efficiency_percent: float

    model_config = ConfigDict(from_attributes=True)

class PumpSchema(BaseModel):
    pump_id: str
    pump_name: str
    motor_kw: float
    max_depth_m: float
    phase_option: str
    flc_1ph_a: Optional[float] = None
    flc_3ph_a: Optional[float] = None
    discharge_size_in: float
    raw_pump_id: str

    model_config = ConfigDict(from_attributes=True)

class PumpDetailSchema(PumpSchema):
    curve: List[CurvePointSchema] = []

class PumpListResponseSchema(BaseModel):
    total_count: int
    pumps: List[PumpSchema]
