from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from backend.database.connection import get_db_connection
from backend.repositories.pump_repository import PumpRepository
from backend.models.pump import PhaseOptionEnum
from backend.api.schemas.pump import PumpSchema, PumpDetailSchema, PumpListResponseSchema, CurvePointSchema

router = APIRouter(prefix="/pumps", tags=["Pumps"])

@router.get("", response_model=PumpListResponseSchema, summary="List Pumps Metadata")
def list_pumps(
    application_type: Optional[str] = Query(None, description="Filter by application type ('borehole' or 'well')"),
    pump_family: Optional[str] = Query(None, description="Filter by pump family (e.g. 'dsd', 'ds')"),
    phase: Optional[str] = Query(None, description="Filter by electrical phase ('1PH', '3PH', '1PH_3PH', '1', '3')"),
    min_motor_kw: Optional[float] = Query(None, ge=0.0, description="Minimum motor power in kW"),
    max_motor_kw: Optional[float] = Query(None, ge=0.0, description="Maximum motor power in kW")
):
    """
    Retrieve pump metadata records from PostgreSQL with optional query filtering.
    """
    # Safely sanitize query string parameters
    clean_pump_family = pump_family.strip() if isinstance(pump_family, str) and pump_family.strip() else None
    clean_app_type = application_type.strip().lower() if isinstance(application_type, str) and application_type.strip() else None
    clean_phase_enum = PhaseOptionEnum.from_raw_string(phase) if isinstance(phase, str) and phase.strip() else None
    clean_min_kw = min_motor_kw if isinstance(min_motor_kw, (int, float)) else None
    clean_max_kw = max_motor_kw if isinstance(max_motor_kw, (int, float)) else None

    try:
        conn = get_db_connection()
        if clean_pump_family:
            all_pumps = PumpRepository.get_pumps_by_family(conn, clean_pump_family)
        elif clean_app_type == "well":
            all_pumps = PumpRepository.get_pumps_by_family(conn, "DSD")
        else:
            all_pumps = PumpRepository.get_all_pumps(conn)
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    # Apply additional Python filters
    filtered_pumps = []
    for p in all_pumps:
        if clean_phase_enum:
            p_phase = p.phase_option
            if clean_phase_enum == PhaseOptionEnum.PHASE_1 and p_phase not in (PhaseOptionEnum.PHASE_1, PhaseOptionEnum.PHASE_1_3):
                continue
            elif clean_phase_enum == PhaseOptionEnum.PHASE_3 and p_phase not in (PhaseOptionEnum.PHASE_3, PhaseOptionEnum.PHASE_1_3):
                continue
            elif clean_phase_enum == PhaseOptionEnum.PHASE_1_3 and p_phase != PhaseOptionEnum.PHASE_1_3:
                continue

        if clean_min_kw is not None and p.motor_kw < clean_min_kw:
            continue
        if clean_max_kw is not None and p.motor_kw > clean_max_kw:
            continue
        filtered_pumps.append(PumpSchema(
            pump_id=p.pump_id,
            pump_name=p.pump_name,
            motor_kw=p.motor_kw,
            max_depth_m=p.max_depth_m,
            phase_option=p.phase_option.value,
            flc_1ph_a=p.flc_1ph_a,
            flc_3ph_a=p.flc_3ph_a,
            discharge_size_in=p.discharge_size_in,
            raw_pump_id=p.raw_pump_id
        ))

    return PumpListResponseSchema(
        total_count=len(filtered_pumps),
        pumps=filtered_pumps
    )

@router.get("/{pump_id}", response_model=PumpDetailSchema, summary="Get Single Pump Metadata & Curve")
def get_pump_by_id(pump_id: str):
    """
    Retrieve single pump metadata and its full array of performance curve points from PostgreSQL.
    """
    clean_id = pump_id.strip().lower()
    try:
        conn = get_db_connection()
        all_pumps = PumpRepository.get_all_pumps(conn)
        matched_pump = next((p for p in all_pumps if p.pump_id == clean_id), None)
        
        if not matched_pump:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Pump with pump_id '{pump_id}' not found.")
            
        curve_points = PumpRepository.get_pump_curves(conn, clean_id)
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    return PumpDetailSchema(
        pump_id=matched_pump.pump_id,
        pump_name=matched_pump.pump_name,
        motor_kw=matched_pump.motor_kw,
        max_depth_m=matched_pump.max_depth_m,
        phase_option=matched_pump.phase_option.value,
        flc_1ph_a=matched_pump.flc_1ph_a,
        flc_3ph_a=matched_pump.flc_3ph_a,
        discharge_size_in=matched_pump.discharge_size_in,
        raw_pump_id=matched_pump.raw_pump_id,
        curve=[
            CurvePointSchema(
                flow_m3h=pt.flow_m3h,
                head_m=pt.head_m,
                efficiency_percent=pt.efficiency_percent
            )
            for pt in curve_points
        ]
    )
