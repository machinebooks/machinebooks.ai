# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# Ejemplo didáctico basado en: ai_service/services/copilot_orchestrator.py
from langchain_core.messages import SystemMessage, HumanMessage

async def rewrite_query_for_rag(
    message: str,
    history: list[dict],
    chat_llm,
) -> str:
    """
    Reformula la query del usuario usando el historial para mejorar
    la búsqueda RAG. Si el mensaje ya es autónomo, lo devuelve tal cual.
    Si es un follow-up ("¿Y los plazos?"), lo expande con contexto.
    """
    # Si no hay historial o el mensaje es largo/autónomo, no reformular
    if not history or len(message.split()) > 15:
        return message

    # Tomar últimos 3 intercambios del historial (6 mensajes)
    recent = history[-6:]
    recent_text = "\n".join(
        f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content'][:200]}"
        for m in recent
    )

    rewrite_messages = [
        SystemMessage(content=(
            "Eres un reformulador de queries para búsqueda semántica. "
            "Dado el historial de conversación y la última pregunta del usuario, "
            "genera una query de búsqueda autónoma y específica que capture "
            "la intención completa. "
            "Responde SOLO con la query reformulada, sin explicaciones. "
            "Si el mensaje ya es autónomo, devuélvelo tal cual."
        )),
        HumanMessage(content=(
            f"Historial reciente:\n{recent_text}\n\n"
            f"Última pregunta: {message}\n\n"
            "Query reformulada para búsqueda:"
        )),
    ]

    response = await chat_llm.ainvoke(rewrite_messages)
    rewritten = response.content.strip()

    if rewritten and len(rewritten) > 5:
        logger.info("query_rewritten",
                     original=message[:60], rewritten=rewritten[:80])
        return rewritten

    return message  # Fallback: usar la query original
