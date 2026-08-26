"""
Prompt Templates Module for RAG & AI Explanation Engine.
Enforces strict instructions: LLM must explain backend results without overriding calculations.
"""

from langchain_core.prompts import PromptTemplate

EXPLAIN_RECOMMENDATION_PROMPT = PromptTemplate(
    template="""Write a direct, confident, and professional technical recommendation to a customer for the pump model {pump_id}.

ENGINEERING DATA:
- Recommended Pump Model: {pump_id}
- Application Type: {application_type}
- Borehole Yield: {yield_m3h} m3/h
- Sustainable Design Flow: {design_flow_m3h} m3/h
- Abstraction Status: {abstraction_status}
- Required Total Dynamic Head (TDH): {tdh_m} m
- Pump Head Capability at Design Flow: {pump_head_m} m
- Head Safety Margin: {head_margin_m} m
- Operating Efficiency: {efficiency_percent}%

MANUFACTURER DATASHEET CONTEXT:
{rag_context}

INSTRUCTIONS:
1. Speak directly and confidently to the customer. DO NOT introduce yourself or state your job title/role (do NOT say "As a Senior Technical Sales Engineer..." or similar). Jump straight into the technical recommendation.
2. Recommend the specific pump model ({pump_id}) confidently using the exact engineering figures provided ({design_flow_m3h} m3/h flow, {yield_m3h} m3/h yield, {tdh_m} m TDH, {pump_head_m} m pump head, {head_margin_m} m head margin, and {efficiency_percent}% efficiency).
3. Explain the sustainable design flow in relation to the tested borehole yield and translate the abstraction status ({abstraction_status}) into customer-friendly terms regarding long-term borehole protection.
4. Explain Total Dynamic Head (TDH), the pump's head capability, and how the head safety margin ensures reliable operation without excessive wear.
5. Highlight the practical benefits of the pump's operating efficiency ({efficiency_percent}%), translating it into energy savings and lower operational costs.
6. Incorporate 1 to 2 specific manufacturer features or material construction facts from the provided datasheet context to reinforce quality and reliability. Never invent manufacturer specifications.
7. FORMAT REQUIREMENT: Produce EXACTLY TWO SHORT PARAGRAPHS.
8. ABSOLUTE PROHIBITION: NEVER mention algorithms, software, deterministic engineering engines, backend processes, databases, RAG, vector stores, AI, prompts, or any internal implementation details. Speak purely and directly to the customer with a practical technical recommendation.
""",
    input_variables=[
        "pump_id", "application_type", "design_flow_m3h", "tdh_m",
        "pump_head_m", "head_margin_m", "efficiency_percent", "yield_m3h",
        "abstraction_status", "rag_context"
    ]
)

ASK_QUESTION_PROMPT = PromptTemplate(
    template="""You are an expert technical documentation assistant for manufacturer pump datasheets.

Answer the user's question directly and concisely using the provided PostgreSQL structured pump data and manufacturer PDF documentation (RAG).

STRICT INSTRUCTIONS:
1. Answer ONLY the specific technical question asked (such as maximum immersion depth, electrical phase options, construction materials, minimum borehole diameter, operating limits, or pump specifications).
2. DO NOT make a pump recommendation, sales pitch, or customer recommendation explanation.
3. DO NOT reference engineering parameters, selected pumps, recommendation logic, or hydraulic calculations unless the user explicitly asked about them.
4. If the provided context contains the answer, summarize it directly and concisely. If the context does not contain enough information to answer, state clearly that the specification is not detailed in the available datasheet excerpts.

USER QUESTION:
{question}

STRUCTURED POSTGRESQL PUMP CONTEXT:
{postgres_context}

MANUFACTURER PDF DATASHEET CONTEXT (RAG):
{rag_context}

Provide a direct, technical answer addressing only the user's question:
""",
    input_variables=["question", "postgres_context", "rag_context"]
)
