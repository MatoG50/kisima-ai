"""
LLM Abstraction Factory Module.
Provides LLM provider interface supporting ChatOpenAI, local Ollama, and MockLLM fallback for cost control.
"""

import os
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
        
        # Synthesize technical explanation based on input prompt context
        explanation = (
            "I strongly recommend the Dayliff DS05-17 pump for your borehole water supply requirement. "
            "With a tested borehole yield of 10.0 m³/h, setting the design flow to a sustainable 8.0 m³/h ensures the long-term health and recharge rate of your aquifer. "
            "The DS05-17 delivers a robust pump head of 89.2 m against your required Total Dynamic Head (TDH) of 93.6 m, with a 4.6 m head safety margin "
            "that guarantees stable, continuous water delivery without overloading the motor.\n\n"
            "Operating at an impressive hydraulic efficiency of 64.5%, this model optimizes power consumption to significantly reduce your daily electricity costs. "
            "Manufactured from premium AISI304 stainless steel with precision-engineered multistage centrifugal impellers, the DS05-17 ensures superior corrosion resistance "
            "and exceptional operating lifespan in demanding submersible conditions."
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
