"""
LangChain RAG Pipeline Orchestration Module.
Coordinates PostgreSQL structured data, LangChain Chroma document retrieval, LLM invocation, and source attribution.
"""

from typing import Dict, Any, Optional
import psycopg2

from backend.rag.metadata import map_pump_id_to_family
from backend.rag.retrieval import retrieve_pump_context
from backend.ai.llm import get_llm_model
from backend.ai.prompts import EXPLAIN_RECOMMENDATION_PROMPT, ASK_QUESTION_PROMPT
from backend.repositories.pump_repository import PumpRepository

def explain_recommendation(recommendation_data: Dict[str, Any], conn=None) -> Dict[str, Any]:
    """
    Generate an AI technical explanation for a structured pump recommendation result.
    Does NOT modify calculated engineering values; explains the backend decision using retrieved RAG datasheets.
    """
    rec_pump = recommendation_data.get("recommended_pump") or {}
    pump_id = rec_pump.get("pump_id") or recommendation_data.get("pump_id") or "UNKNOWN"
    
    app_type = recommendation_data.get("application_type", "borehole")
    design_flow = recommendation_data.get("design_flow_m3h") or rec_pump.get("design_flow_m3h") or 0.0
    tdh = rec_pump.get("required_tdh_m") or recommendation_data.get("tdh_m") or 0.0
    pump_head = rec_pump.get("pump_head_at_design_flow_m") or recommendation_data.get("pump_head_m") or 0.0
    margin = rec_pump.get("head_margin_m") or recommendation_data.get("head_margin_m") or 0.0
    eta = rec_pump.get("operating_efficiency_percent") or recommendation_data.get("efficiency_percent") or 0.0
    bh_yield = recommendation_data.get("yield_m3h") or 0.0
    status_abs = recommendation_data.get("abstraction_status") or "SUSTAINABLE"

    # Map pump ID to pump family (e.g. ds05-17 -> DS5)
    pump_family = map_pump_id_to_family(pump_id)
    
    # Retrieve RAG context from Chroma
    rag_res = retrieve_pump_context(
        query=f"{pump_family} datasheet technical specification installation application",
        pump_family=pump_family,
        k=3
    )

    # Format LangChain prompt
    prompt = EXPLAIN_RECOMMENDATION_PROMPT.format(
        pump_id=pump_id,
        application_type=app_type,
        design_flow_m3h=design_flow,
        tdh_m=tdh,
        pump_head_m=pump_head,
        head_margin_m=margin,
        efficiency_percent=eta,
        yield_m3h=bh_yield,
        abstraction_status=status_abs,
        rag_context=rag_res["context_text"]
    )

    # Call LLM
    llm = get_llm_model()
    llm_output = llm.invoke(prompt)
    answer_text = llm_output.content if hasattr(llm_output, 'content') else str(llm_output)

    return {
        "answer": answer_text,
        "pump_id": pump_id,
        "pump_family": pump_family,
        "sources": rag_res["sources"]
    }

def ask_question(question: str, pump_id: Optional[str] = None, conn=None) -> Dict[str, Any]:
    """
    Answer user technical Q&A using RAG datasheet retrieval and PostgreSQL structured data context.
    """
    postgres_context_str = "No specific pump model selected."
    pump_family = None

    if pump_id and conn:
        try:
            p_obj = PumpRepository.get_all_pumps(conn)
            match_p = next((p for p in p_obj if p.pump_id == pump_id.strip().lower()), None)
            if match_p:
                pump_family = map_pump_id_to_family(match_p.pump_id)
                postgres_context_str = (
                    f"Selected Pump: {match_p.pump_name} (ID: {match_p.pump_id})\n"
                    f"Motor Power: {match_p.motor_kw} kW | Max Submersion Depth: {match_p.max_depth_m} m\n"
                    f"Discharge Size: {match_p.discharge_size_in} in | Electrical Phase: {match_p.phase_option.value}"
                )
        except Exception:
            pass
    elif pump_id:
        pump_family = map_pump_id_to_family(pump_id)

    # Retrieve RAG context from Chroma
    rag_res = retrieve_pump_context(
        query=question,
        pump_family=pump_family,
        k=3
    )

    # Format LangChain prompt
    prompt = ASK_QUESTION_PROMPT.format(
        question=question,
        postgres_context=postgres_context_str,
        rag_context=rag_res["context_text"]
    )

    # Call LLM
    llm = get_llm_model()
    llm_output = llm.invoke(prompt)
    answer_text = llm_output.content if hasattr(llm_output, 'content') else str(llm_output)

    return {
        "answer": answer_text,
        "pump_id": pump_id,
        "sources": rag_res["sources"]
    }
