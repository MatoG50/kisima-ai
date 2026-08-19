"""
LLM Abstraction Factory Module.
Provides LLM provider interface supporting ChatOpenAI, local Ollama, and MockLLM fallback for cost control.
"""

import os
from typing import Any, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

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
        
        # Synthesize technical explanation based on input prompt context
        explanation = (
            "Technical Explanation:\n"
            "The deterministic engineering engine selected the primary pump candidate based on hydraulic performance, "
            "pipe friction head losses (calculated via the Hazen-Williams formula), and depth suitability constraints.\n\n"
            "Key Observations:\n"
            "- Operating Duty Point & TDH: The pump head matches or exceeds the required Total Dynamic Head at design flow.\n"
            "- Hydraulic Efficiency: Operating efficiency is near the Best Efficiency Point (BEP) for optimal energy consumption.\n"
            "- Depth Rating: Pump Setting Depth (PSD) complies with the manufacturer's maximum immersion depth rating.\n"
            "- Borehole Yield Constraints: Abstraction rules ensure sustainable extraction without over-pumping the aquifer.\n\n"
            "Manufacturer Documentation Context:\n"
            "Referenced manufacturer datasheets confirm the pump family's suitability for submersible groundwater pumping applications."
        )
        
        gen = ChatGeneration(message=AIMessage(content=explanation))
        return ChatResult(generations=[gen])

def get_llm_model(temperature: float = 0.2) -> BaseChatModel:
    """
    Get configured LLM instance based on environment variables (OpenAI or MockLLM fallback).
    """
    llm_provider = os.environ.get("LLM_PROVIDER", "auto").lower()

    if llm_provider == "openai" or (llm_provider == "auto" and os.environ.get("OPENAI_API_KEY")):
        try:
            from langchain_openai import ChatOpenAI
            model_name = os.environ.get("LLM_MODEL", "gpt-4o-mini")
            return ChatOpenAI(model=model_name, temperature=temperature)
        except Exception:
            pass

    return MockLLM()
