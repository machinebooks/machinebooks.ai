# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# Antes: llamada directa al SDK
# llm = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=2048)

# Después: tracker transparente
from services.llm_usage_tracker import LLMUsageTracker
from langchain_anthropic import ChatAnthropic

async def analyze_document(content: str, user_id: str) -> str:
    """
    Análisis documental con tracking automático de coste.
    El código de negocio no cambia salvo la instanciación.
    """
    llm = LLMUsageTracker(
        base_llm=ChatAnthropic(model="claude-sonnet-4-6", max_tokens=4096),
        service_name="analyze_document",
        calling_app="document_analyzer",
        user_id=user_id,
        prompt_key="document_analysis_v3",
    )

    messages = [
        SystemMessage(content=ANALYSIS_PROMPT),
        HumanMessage(content=content),
    ]

    # La llamada es idéntica a la del SDK nativo
    response = await llm.ainvoke(messages)
    return response.content
