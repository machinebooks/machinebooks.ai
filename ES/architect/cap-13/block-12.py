# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
from intent_classifier import clasificar_intent, TipoIntent
from oportunidades_search import buscar_oportunidades

def procesar_consulta_usuario(
    consulta: str,
    contexto_usuario: dict,
    rag_engine,         # Inyectado por el contenedor de dependencias
    workflow_engine,    # Inyectado por el contenedor de dependencias
) -> dict:
    """
    Enrutador principal de consultas.
    Clasifica la intención y delega al motor apropiado.
    """
    intent = clasificar_intent(consulta)

    # Registrar la clasificación para análisis de calidad
    log_intent_classification(
        consulta=consulta,
        intent=intent.tipo.value,
        confianza=intent.confianza,
        capa_usada="capa1" if intent.razonamiento == "" else "capa2",
        usuario_id=contexto_usuario.get("user_id"),
    )

    if intent.tipo == TipoIntent.AGENT_TOOLS and intent.subtipo == "search_opportunities":
        # Extraer parámetros de búsqueda del texto de la consulta
        # En producción esto se enriquece con un extractor de entidades
        params = extraer_parametros_busqueda(consulta)
        resultados = buscar_oportunidades(**params)
        return {
            "tipo": "search_results",
            "motor": "meilisearch",
            "intent_confianza": intent.confianza,
            "datos": resultados,
        }

