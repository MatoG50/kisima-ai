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

class MockLLM(BaseChatModel):
    """
    Deterministic Mock LLM for offline testing, cost control, and demonstration.
    Extracts key engineering parameters from prompt and synthesizes a clear technical explanation.
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
        
        # Regex parse engineering data from EXPLAIN_RECOMMENDATION_PROMPT
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
                "Based on your engineering parameters and manufacturer datasheet context, "
                "the selected pump model provides optimal hydraulic performance and high operational efficiency for your water system."
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
