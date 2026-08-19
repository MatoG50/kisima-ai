from fastapi import APIRouter
from backend.database.connection import get_db_connection

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Health Check Endpoint")
def get_health():
    """
    Check API operational health and PostgreSQL database connectivity.
    """
    db_status = "disconnected"
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "database": db_status
    }
