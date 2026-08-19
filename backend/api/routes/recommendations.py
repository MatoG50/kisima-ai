from fastapi import APIRouter, HTTPException
from backend.database.connection import get_db_connection
from backend.selection.service import PumpRecommendationService
from backend.api.schemas.recommendation import RecommendationRequestSchema, RecommendationResponseSchema

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("/pump", response_model=RecommendationResponseSchema, summary="Evaluate Pump Candidates & Recommend Primary Pump")
def recommend_pump(req: RecommendationRequestSchema):
    """
    Primary REST API recommendation endpoint.
    Parses request, calls PumpRecommendationService, and returns structured recommendation.
    """
    try:
        conn = get_db_connection()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection unavailable: {str(e)}"
        )

    try:
        app_type = req.application_type.lower()
        if app_type == "borehole":
            res_dict = PumpRecommendationService.recommend_borehole(
                conn=conn,
                yield_m3h=req.yield_m3h,
                pwl_m=req.pwl_m,
                psd_m=req.psd_m,
                customer_requested_flow_m3h=req.customer_requested_flow_m3h,
                delivery_distance_m=req.delivery_distance_m,
                destination_elevation_m=req.destination_elevation_m
            )
        elif app_type == "well":
            res_dict = PumpRecommendationService.recommend_well(
                conn=conn,
                static_head_m=req.static_head_m,
                customer_requested_flow_m3h=req.customer_requested_flow_m3h,
                delivery_distance_m=req.delivery_distance_m,
                default_pump_family=req.default_pump_family
            )
        else:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Unsupported application_type '{req.application_type}'.")

        conn.close()
        return res_dict

    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Internal recommendation service error: {str(e)}"
        )
