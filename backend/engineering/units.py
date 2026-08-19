"""
Engineering Unit Conversions and Constants Module.
All conversion factors are explicit, standard SI engineering values.
"""

# Inches to meters conversion factor (exact: 1 inch = 0.0254 m)
INCHES_TO_METERS: float = 0.0254

# Cubic meters per hour to cubic meters per second (3600 seconds/hour)
M3H_TO_M3S: float = 1.0 / 3600.0

# Standard acceleration due to gravity (m/s^2)
GRAVITY_M_S2: float = 9.81

def inches_to_meters(inches: float) -> float:
    """Convert pipe diameter from inches to meters."""
    if inches <= 0:
        raise ValueError(f"Pipe diameter in inches must be positive, got {inches}")
    return float(inches) * INCHES_TO_METERS

def m3h_to_m3s(flow_m3h: float) -> float:
    """Convert volumetric flow rate from m^3/h to m^3/s."""
    if flow_m3h < 0:
        raise ValueError(f"Flow rate in m3/h cannot be negative, got {flow_m3h}")
    return float(flow_m3h) * M3H_TO_M3S

def m3s_to_m3h(flow_m3s: float) -> float:
    """Convert volumetric flow rate from m^3/s to m^3/h."""
    if flow_m3s < 0:
        raise ValueError(f"Flow rate in m3/s cannot be negative, got {flow_m3s}")
    return float(flow_m3s) / M3H_TO_M3S
