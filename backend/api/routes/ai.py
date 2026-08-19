from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from backend.database.connection import get_db_connection
from backend.ai.rag import explain_recommendation, ask_question

router = APIRouter(prefix="/ai", tags=["AI Explanation & Knowledge Layer"])

class SourceCitationSchema(BaseModel):
    document: str
    pump_family: Optional[str] = None
    page: Optional[int] = 1
    chunk_snippet: Optional[str] = None

class ExplainRequestSchema(BaseModel):
    pump_id: str = Field(..., description="Recommended pump ID (e.g. 'ds05-17')")
    application_type: str = Field("borehole", description="Application type: 'borehole' or 'well'")
    design_flow_m3h: float = Field(..., gt=0.0, description="Operating design flow rate in m3/h")
    tdh_m: float = Field(..., gt=0.0, description="Required Total Dynamic Head in meters")
    pump_head_m: Optional[float] = Field(None, description="Pump head capability at design flow in meters")
    efficiency_percent: Optional[float] = Field(None, description="Operating efficiency percent")
    head_margin_m: Optional[float] = Field(None, description="Head margin over TDH in meters")
    yield_m3h: Optional[float] = Field(None, description="Borehole yield in m3/h")
    abstraction_status: Optional[str] = Field("SUSTAINABLE", description="Abstraction status")

class ExplainResponseSchema(BaseModel):
    answer: str
    pump_id: str
    pump_family: str
    sources: List[SourceCitationSchema] = []

class AskRequestSchema(BaseModel):
    question: str = Field(..., min_length=3, description="Technical engineering or datasheet question")
    pump_id: Optional[str] = Field(None, description="Optional pump_id context (e.g. 'ds05-17')")

class AskResponseSchema(BaseModel):
    answer: str
    pump_id: Optional[str] = None
    sources: List[SourceCitationSchema] = []

@router.post("/explain", response_model=ExplainResponseSchema, summary="Explain Pump Recommendation Result using RAG Context")
def explain_pump_recommendation(req: ExplainRequestSchema):
    """
    Generate an AI technical explanation for a structured pump recommendation result.
    Uses retrieved manufacturer PDF datasheet context without modifying calculated backend values.
    """
    try:
        conn = get_db_connection()
    except Exception:
        conn = None

    try:
        res = explain_recommendation(req.model_dump(), conn=conn)
        if conn:
            conn.close()
        return res
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(status_code=500, detail=f"AI explanation generation error: {str(e)}")

@router.post("/ask", response_model=AskResponseSchema, summary="Ask Technical Question about Pump Sizing or Manufacturer Datasheets")
def ask_technical_question(req: AskRequestSchema):
    """
    Answer a technical engineering question using RAG datasheet retrieval and PostgreSQL pump context.
    """
    try:
        conn = get_db_connection()
    except Exception:
        conn = None

    try:
        res = ask_question(question=req.question, pump_id=req.pump_id, conn=conn)
        if conn:
            conn.close()
        return res
    except Exception as e:
        if conn:
            conn.close()
        raise HTTPException(status_code=500, detail=f"AI Q&A processing error: {str(e)}")
