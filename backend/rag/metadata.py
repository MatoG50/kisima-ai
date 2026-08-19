"""
Metadata Extractor Module for RAG Document Ingestion.
Maps PDF filenames and PostgreSQL pump IDs to canonical pump family names.
"""

import os
import re
from typing import Dict, Any

def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract structured metadata from a PDF datasheet file path.
    Example: 'data/documents/ds5.pdf' -> pump_family: 'DS5'
    """
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0].lower().strip()
    
    # Standardize family name (e.g. ds5 -> DS5, dsd3 -> DSD3, dsp1 -> DSP1, dss14 -> DSS14)
    family_name = base_name.upper()
    
    return {
        "source_file": filename,
        "pump_family": family_name,
        "document_type": "pump_datasheet"
    }

def map_pump_id_to_family(pump_id: str) -> str:
    """
    Map a specific PostgreSQL pump_id (e.g., 'ds05-17', 'dsd03-07') to its datasheet pump family ('DS5', 'DSD3').
    """
    clean_id = pump_id.strip().lower()
    
    # Match patterns like dsd03-07 -> DSD3, dss05-17 -> DSS5, ds05-17 -> DS5, dsp01-05 -> DSP1
    match = re.match(r"^([a-z]+)0*(\d+)", clean_id)
    if match:
        prefix = match.group(1).upper() # e.g. DSD, DSS, DS, DSP
        number = str(int(match.group(2))) # e.g. 05 -> 5, 03 -> 3
        return f"{prefix}{number}"
    
    return clean_id.split("-")[0].upper()
