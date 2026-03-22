# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
# Ejemplo didáctico: patrones/tools/tool_description_patterns.py

# MAL: descripción genérica que confunde al agente
bad_tool = {
    "name": "search",
    "description": "Busca información en el sistema",
    # Claude no sabe si buscar en Qdrant, Meilisearch o BD
}

# BIEN: descripción prescriptiva con contexto de uso
good_tool = {
    "name": "search_documents",
    "description": (
        "Busca documentos por similitud semántica en la base de conocimiento interna. "
        "Usar cuando el usuario pregunta sobre propuestas anteriores, documentos de "
        "requisitos, CVs almacenados o cualquier contenido que ya existe en el sistema. "
        "NO usar para buscar oportunidades públicas (usar search_opportunities para eso)."
    ),
}
