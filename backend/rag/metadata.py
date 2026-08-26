"""
Metadata Extractor Module for RAG Document Ingestion.
Maps PDF filenames, PostgreSQL pump IDs, and user natural language queries to canonical pump families and family prefixes.
"""

import os
import re
from typing import Dict, Any, Optional, Tuple

SUPPORTED_PREFIXES = ["DSS", "DSD", "DSP", "DS"]

def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract structured metadata from a PDF datasheet file path.
    Example: 'data/documents/ds5.pdf' -> pump_family: 'DS5', family_prefix: 'DS'
    """
    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0].lower().strip()
    
    # Standardize family name (e.g. ds5 -> DS5, dsd3 -> DSD3, dsp1 -> DSP1, dss14 -> DSS14)
    family_name = base_name.upper()
    family_prefix = extract_family_prefix(family_name)
    
    return {
        "source_file": filename,
        "pump_family": family_name,
        "family_prefix": family_prefix,
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

def extract_family_prefix(text: str) -> str:
    """
    Extract canonical family prefix (DSS, DSD, DSP, or DS) from a pump family string or model ID.
    Always tests 3-letter prefixes (DSS, DSD, DSP) before 2-letter prefix (DS).
    """
    clean_text = text.strip().upper()
    for prefix in ["DSS", "DSD", "DSP", "DS"]:
        if clean_text.startswith(prefix):
            return prefix
    return clean_text

def detect_pump_family_from_query(query: str, pump_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect exact pump_family (e.g. 'DSS14') and/or family_prefix (e.g. 'DSS') from prompt or explicit pump_id.
    Returns tuple (pump_family, family_prefix).
    """
    detected_family: Optional[str] = None
    detected_prefix: Optional[str] = None

    if pump_id:
        detected_family = map_pump_id_to_family(pump_id)
        detected_prefix = extract_family_prefix(detected_family)

    if query:
        # 1. Match specific family + model number pattern (e.g. DSS14, DSD3, DS5, DSP1, XYZ999)
        model_match = re.search(r"\b([a-zA-Z]+)0*(\d+)\b", query, re.IGNORECASE)
        if model_match:
            prefix = model_match.group(1).upper()
            number = str(int(model_match.group(2)))
            detected_family = f"{prefix}{number}"
            detected_prefix = prefix
            return detected_family, detected_prefix

        # 2. Match standalone family prefix (e.g. "DSS pump", "DSD series", "DSP", "DS")
        prefix_match = re.search(r"\b(DSS|DSD|DSP|DS)\b", query, re.IGNORECASE)
        if prefix_match:
            detected_prefix = prefix_match.group(1).upper()
            if not detected_family or not detected_family.startswith(detected_prefix):
                detected_family = None
            return detected_family, detected_prefix

    return detected_family, detected_prefix
