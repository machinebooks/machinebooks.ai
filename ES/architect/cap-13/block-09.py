# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def clasificar_intent_capa1(consulta: str) -> IntentResult | None:
    """
    Capa 1: pattern matching determinista.
    Devuelve None si la confianza no supera el umbral.
    """
    consulta_lower = consulta.lower()

    # Evaluar en orden de prioridad — WORKFLOW antes que SEARCH
    # para evitar que "genera una propuesta" acabe en búsqueda
    checks = [
        (PATRONES_OFF_TOPIC, TipoIntent.OFF_TOPIC, ""),
        (PATRONES_WORKFLOW, TipoIntent.WORKFLOW, "generate_proposal"),
        (PATRONES_SEARCH_OPORTUNIDADES, TipoIntent.AGENT_TOOLS, "search_opportunities"),
        (PATRONES_RAG, TipoIntent.CHAT_RAG, "rag_query"),
    ]

    for patrones, tipo, subtipo in checks:
        coincidencias = sum(
            1 for patron in patrones
            if re.search(patron, consulta_lower)
        )
        if coincidencias >= 2:
            # Dos o más patrones coincidentes → alta confianza
            return IntentResult(tipo=tipo, confianza=0.92, subtipo=subtipo)
        elif coincidencias == 1:
            # Un patrón coincidente → confianza moderada
            # Solo retornamos si supera el umbral
            confianza = 0.78
            if confianza >= UMBRAL_CONFIANZA_CAPA1:
                return IntentResult(tipo=tipo, confianza=confianza, subtipo=subtipo)

    return None  # Confianza insuficiente → activar capa 2


