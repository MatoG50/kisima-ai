"""
Hazen-Williams Pipe Friction Loss Calculation Module.
Implements standard SI hydraulic equations for head loss and fluid velocity.
"""

import math
from typing import Union
from backend.engineering.units import inches_to_meters, m3h_to_m3s
from backend.engineering.materials import PipeMaterial, get_pipe_material

def calculate_hazen_williams_friction(
    length_m: float,
    flow_m3h: float,
    diameter_in: float,
    material: Union[str, PipeMaterial]
) -> float:
    """
    Calculate friction head loss (h_f) in meters using the Hazen-Williams formula in SI units:
    
        h_f = 10.67 * L * (Q^1.852) / (C^1.852 * D^4.871)
        
    Parameters:
    - length_m: Pipe length in meters (L >= 0)
    - flow_m3h: Flow rate in cubic meters per hour (Q >= 0)
    - diameter_in: Internal pipe diameter in inches (D > 0)
    - material: Material name string ('uPVC', 'HDPE') or PipeMaterial instance
    
    Returns:
    - Head loss in meters (float, >= 0.0)
    """
    if length_m < 0:
        raise ValueError(f"Pipe length cannot be negative, got {length_m} m")
    if flow_m3h < 0:
        raise ValueError(f"Flow rate cannot be negative, got {flow_m3h} m3/h")
    
    # If length or flow is zero, friction loss is 0.0
    if length_m == 0.0 or flow_m3h == 0.0:
        return 0.0

    if isinstance(material, str):
        pipe_mat = get_pipe_material(material)
    elif isinstance(material, PipeMaterial):
        pipe_mat = material
    else:
        raise ValueError(f"Invalid material specification: {material}")

    c_factor = pipe_mat.hazen_williams_c
    if c_factor <= 0:
        raise ValueError(f"Hazen-Williams C coefficient must be positive, got {c_factor}")

    diameter_m = inches_to_meters(diameter_in)
    flow_m3s = m3h_to_m3s(flow_m3h)

    # Hazen-Williams formula SI constant: 10.67
    numerator = 10.67 * length_m * (flow_m3s ** 1.852)
    denominator = (c_factor ** 1.852) * (diameter_m ** 4.871)

    hf_m = numerator / denominator
    return float(hf_m)

def calculate_pipe_velocity(flow_m3h: float, diameter_in: float) -> float:
    """
    Calculate average fluid velocity in pipe: v = Q / A = (4 * Q) / (pi * D^2) in m/s.
    """
    if flow_m3h < 0:
        raise ValueError(f"Flow rate cannot be negative, got {flow_m3h} m3/h")
    if flow_m3h == 0.0:
        return 0.0
        
    diameter_m = inches_to_meters(diameter_in)
    flow_m3s = m3h_to_m3s(flow_m3h)
    area_m2 = (math.pi * (diameter_m ** 2)) / 4.0
    return float(flow_m3s / area_m2)
