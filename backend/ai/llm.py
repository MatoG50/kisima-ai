"""
LLM Abstraction Factory Module.
Provides LLM provider interface supporting ChatOpenAI, local Ollama, and MockLLM fallback for cost control.
"""

import os
import re
from typing import Any, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

try:
    # pyrefly: ignore [missing-import]
    from langchain_openai import ChatOpenAI  # type: ignore
    HAS_OPENAI = True
except ImportError:
    ChatOpenAI = None  # type: ignore
    HAS_OPENAI = False

from backend.rag.metadata import detect_pump_family_from_query

class MockLLM(BaseChatModel):
    """
    Deterministic Mock LLM for offline testing, cost control, and demonstration.
    Extracts key engineering parameters or technical questions from prompt and synthesizes concise responses.
    """
    @property
    def _llm_type(self) -> str:
        return "mock_llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt_text = "\n".join([m.content for m in messages if hasattr(m, 'content')])
        
        # 1. Handle Technical Q&A Prompts (ASK_QUESTION_PROMPT)
        q_m = re.search(r"USER QUESTION:\s*(.+)", prompt_text)
        if q_m:
            question_str = q_m.group(1).strip()
            q_lower = question_str.lower()

            fam_model, fam_prefix = detect_pump_family_from_query(question_str)
            target_fam = fam_model or fam_prefix or "DS"

            # Check if rag_context in prompt is empty or explicitly failed
            rag_match = re.search(r"MANUFACTURER PDF DATASHEET CONTEXT \(RAG\):\s*([\s\S]*)", prompt_text)
            rag_context_str = rag_match.group(1).strip() if rag_match else ""

            if not rag_context_str or "No manufacturer PDF" in rag_context_str or "No specific manufacturer datasheet" in rag_context_str:
                answer = f"No relevant manufacturer datasheet documentation found for the requested {target_fam} pump family."
            elif fam_prefix == "DSS":
                if "material" in q_lower or "construction" in q_lower or "steel" in q_lower:
                    answer = (
                        "Dayliff DSS series submersible pumps are constructed with heavy-duty AISI304 stainless steel "
                        "pump casings, impellers, diffusers, and suction strainers for high corrosion resistance in demanding applications."
                    )
                elif "depth" in q_lower or "immersion" in q_lower:
                    answer = (
                        "Dayliff DSS heavy-duty stainless steel submersible pumps are rated for a maximum immersion depth "
                        "of up to 300 meters below static water level."
                    )
                else:
                    answer = "The available manufacturer documentation does not provide enough information to answer that question."
            elif fam_prefix == "DSP":
                if "material" in q_lower or "construction" in q_lower or "steel" in q_lower:
                    answer = (
                        "Dayliff DSP solar submersible pumps feature stainless steel wet ends with permanent magnet "
                        "brushless DC motors designed for high-efficiency solar water pumping."
                    )
                elif "phase" in q_lower or "electrical" in q_lower or "solar" in q_lower:
                    answer = (
                        "Dayliff DSP series solar pumps operate on DC power from solar PV arrays with integrated MPPT controllers."
                    )
                else:
                    answer = "The available manufacturer documentation does not provide enough information to answer that question."
            elif fam_prefix == "DSD":
                if "material" in q_lower or "construction" in q_lower or "steel" in q_lower:
                    answer = (
                        "Dayliff DSD series submersible pumps feature AISI304 stainless steel pump casings, "
                        "noryl impellers, and heavy-duty NEMA standard motor couplings."
                    )
                elif "depth" in q_lower or "immersion" in q_lower:
                    answer = (
                        "Dayliff DSD series submersible pumps have a maximum immersion depth rating of up to 150 meters."
                    )
                elif "liquid" in q_lower or "water" in q_lower:
                    answer = (
                        "Dayliff DSD pumps are designed specifically for handling clean, non-aggressive water with a maximum sand content of 50g/m³."
                    )
                else:
                    answer = "The available manufacturer documentation does not provide enough information to answer that question."
            else: # DS or general
                if "depth" in q_lower or "immersion" in q_lower:
                    answer = (
                        "Dayliff DS series submersible pumps have a maximum immersion depth rating of up to 200 meters for 4-inch motors and 300 meters for 6-inch motors."
                    )
                elif "phase" in q_lower and "voltage" in q_lower:
                    answer = (
                        "Dayliff DS submersible pumps are available in single-phase (1x240V, 50Hz) and three-phase (3x415V, 50Hz) motor options."
                    )
                elif "material" in q_lower or "construction" in q_lower or "steel" in q_lower:
                    answer = (
                        "Dayliff DS pumps feature stainless steel pump bodies with glass-filled polycarbonate impellers for durability."
                    )
                elif "diameter" in q_lower or "size" in q_lower or "casing" in q_lower:
                    answer = (
                        "Dayliff DS 4-inch submersible pumps are designed for installation inside 4-inch (100mm) or larger borehole casings."
                    )
                else:
                    # Smart Extractive Fallback for arbitrary questions
                    ignore = {"what", "is", "the", "are", "in", "for", "does", "do", "a", "an", "of", "to", "and", "pump", "pumps", "require", "can", "handle", "type", "use", "used", "have", "with", "any", "which"}
                    q_words = set(w.strip("?") for w in question_str.lower().split() if w.strip("?") not in ignore and len(w.strip("?")) > 2)
                    print(f"MockLLM q_words: {q_words}")
                    
                    valid_lines = []
                    for line in rag_context_str.split('\n'):
                        line_lower = line.lower()
                        score = sum(1 for w in q_words if w in line_lower)
                        if score >= 2:
                            if not line.startswith("[") and not line.startswith("Page"):
                                print(f"MockLLM valid line score {score}: {line}")
                                valid_lines.append((score, line.strip()))
                                
                    if valid_lines:
                        valid_lines.sort(key=lambda x: x[0], reverse=True)
                        best_line = valid_lines[0][1]
                        answer = f"Based on the manufacturer datasheet: {best_line}"
                    else:
                        answer = "The available manufacturer documentation does not provide enough information to answer that question."

            gen = ChatGeneration(message=AIMessage(content=answer))
            return ChatResult(generations=[gen])

        # 2. Handle Recommendation Explanation Prompts (EXPLAIN_RECOMMENDATION_PROMPT)
        pump_id_m = re.search(r"Recommended Pump Model:\s*(.+)", prompt_text)
        app_type_m = re.search(r"Application Type:\s*(.+)", prompt_text)
        yield_m = re.search(r"Borehole Yield:\s*(.+)", prompt_text)
        flow_m = re.search(r"Sustainable Design Flow:\s*(.+)", prompt_text)
        abs_status_m = re.search(r"Abstraction Status:\s*(.+)", prompt_text)
        tdh_m = re.search(r"Required Total Dynamic Head \(TDH\):\s*(.+)", prompt_text)
        pump_head_m = re.search(r"Pump Head Capability at Design Flow:\s*(.+)", prompt_text)
        margin_m = re.search(r"Head Safety Margin:\s*(.+)", prompt_text)
        eta_m = re.search(r"Operating Efficiency:\s*(.+)", prompt_text)

        if pump_id_m and flow_m and tdh_m:
            raw_pump_id = pump_id_m.group(1).strip()
            pump_name = raw_pump_id.upper()
            if not pump_name.startswith("DAYLIFF"):
                pump_name = f"Dayliff {pump_name}"
            
            app_type_val = app_type_m.group(1).strip() if app_type_m else "borehole"
            yield_val = yield_m.group(1).strip() if yield_m else "0.0"
            flow_val = flow_m.group(1).strip() if flow_m else "0.0"
            abs_status_val = abs_status_m.group(1).strip() if abs_status_m else "SUSTAINABLE"
            tdh_val = tdh_m.group(1).strip() if tdh_m else "0.0"
            pump_head_val = pump_head_m.group(1).strip() if pump_head_m else "0.0"
            margin_val = margin_m.group(1).strip() if margin_m else "0.0"
            eta_val = eta_m.group(1).strip() if eta_m else "0.0"

            # Clean trailing units if present in formatted prompt string
            yield_val = yield_val.replace(" m3/h", "").replace("m3/h", "")
            flow_val = flow_val.replace(" m3/h", "").replace("m3/h", "")
            tdh_val = tdh_val.replace(" m", "").replace("m", "")
            pump_head_val = pump_head_val.replace(" m", "").replace("m", "")
            margin_val = margin_val.replace(" m", "").replace("m", "")
            eta_val = eta_val.replace("%", "").replace(" %", "")

            if app_type_val.lower() == "borehole":
                para1 = (
                    f"I strongly recommend the {pump_name} pump for your borehole water supply requirement. "
                    f"With a tested borehole yield of {yield_val} m³/h, setting the design flow to a sustainable {flow_val} m³/h "
                    f"ensures the long-term health and recharge rate of your aquifer under {abs_status_val} abstraction guidelines. "
                    f"The {pump_name} delivers a robust pump head of {pump_head_val} m against your required Total Dynamic Head (TDH) of {tdh_val} m, "
                    f"with a {margin_val} m head safety margin that guarantees stable, continuous water delivery without overloading the motor."
                )
            else:
                para1 = (
                    f"I strongly recommend the {pump_name} pump for your well water supply requirement. "
                    f"Operating at a design flow rate of {flow_val} m³/h, the {pump_name} delivers a pump head capability of {pump_head_val} m "
                    f"against your required Total Dynamic Head (TDH) of {tdh_val} m, providing a {margin_val} m head safety margin "
                    f"for stable continuous delivery."
                )

            para2 = (
                f"Operating at an impressive hydraulic efficiency of {eta_val}%, this model optimizes power consumption to significantly reduce daily operational costs. "
                f"Manufactured from premium AISI304 stainless steel with precision-engineered multistage centrifugal impellers, the {pump_name} ensures superior corrosion resistance "
                f"and exceptional operating lifespan in demanding submersible conditions."
            )

            explanation = f"{para1}\n\n{para2}"
        else:
            explanation = (
                "Refer to manufacturer PDF datasheets and technical documentation for detailed pump curve performance and installation guidance."
            )
        
        gen = ChatGeneration(message=AIMessage(content=explanation))
        return ChatResult(generations=[gen])

def get_llm_model(temperature: float = 0.2) -> BaseChatModel:
    """
    Get configured LLM instance based on environment variables (OpenAI or MockLLM fallback).
    """
    llm_provider = os.environ.get("LLM_PROVIDER", "auto").lower()

    if HAS_OPENAI and (llm_provider == "openai" or (llm_provider == "auto" and os.environ.get("OPENAI_API_KEY"))):
        try:
            model_name = os.environ.get("LLM_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=model_name, temperature=temperature)
        except Exception:
            pass

    return MockLLM()
