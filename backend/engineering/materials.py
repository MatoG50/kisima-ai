"""
Pipe Materials and Hazen-Williams Roughness Coefficients Module.
Default coefficients adhere to standard hydraulic engineering tables for clean plastic pipes.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class PipeMaterial:
    name: str
    hazen_williams_c: float
    description: str

# Standard Material Registry
PRESET_MATERIALS: Dict[str, PipeMaterial] = {
    "UPVC": PipeMaterial(
        name="uPVC",
        hazen_williams_c=150.0,
        description="Unplasticized Polyvinyl Chloride (smooth plastic riser pipe)"
    ),
    "HDPE": PipeMaterial(
        name="HDPE",
        hazen_williams_c=140.0,
        description="High-Density Polyethylene (flexible surface delivery pipe)"
    ),
    "STEEL": PipeMaterial(
        name="Steel",
        hazen_williams_c=120.0,
        description="Galvanized steel pipe"
    ),
    "CAST_IRON": PipeMaterial(
        name="Cast Iron",
        hazen_williams_c=100.0,
        description="Unlined cast iron pipe"
    )
}

def get_pipe_material(material_name: str) -> PipeMaterial:
    """
    Retrieve pipe material by name (case-insensitive).
    Raises ValueError if material is unknown.
    """
    if not material_name:
        raise ValueError("Material name cannot be empty.")
    key = str(material_name).strip().upper()
    if key in PRESET_MATERIALS:
        return PRESET_MATERIALS[key]
    raise ValueError(f"Unknown pipe material '{material_name}'. Supported materials: {list(PRESET_MATERIALS.keys())}")
