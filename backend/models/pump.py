from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class PhaseOptionEnum(str, Enum):
    PHASE_1 = "1PH"
    PHASE_3 = "3PH"
    PHASE_1_3 = "1PH_3PH"

    @classmethod
    def from_raw_string(cls, val: Optional[str]) -> Optional['PhaseOptionEnum']:
        if val is None:
            return None
        s = str(val).strip()
        if s in ['1,3', '1, 3', '1/3', '1PH_3PH']:
            return cls.PHASE_1_3
        elif s in ['1', '1PH']:
            return cls.PHASE_1
        elif s in ['3', '3PH']:
            return cls.PHASE_3
        return None

@dataclass
class PumpModel:
    pump_id: str             # Normalized lowercase ID (e.g. 'ds02-09')
    pump_name: str           # Commercial name (e.g. 'dayliff ds2/9')
    motor_kw: float          # Motor power rating in kW
    max_depth_m: float       # Maximum depth in meters
    phase_option: PhaseOptionEnum # Phase enum ('1PH', '3PH', '1PH_3PH')
    flc_1ph_a: Optional[float]    # Full load current 1x240V (Amperes)
    flc_3ph_a: Optional[float]    # Full load current 3x415V (Amperes)
    discharge_size_in: float      # Outlet pipe size in inches
    raw_pump_id: str         # Original string from Excel

@dataclass
class PumpCurvePoint:
    pump_id: str             # FK referencing PumpModel.pump_id
    flow_m3h: float          # Flow rate in m3/h
    head_m: float            # Head in meters
    efficiency_percent: float # Hydraulic efficiency %
    id: Optional[int] = None
