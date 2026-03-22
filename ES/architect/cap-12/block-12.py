# Extraído de: LibroTecnico/cap-12-rag-produccion.md
# En el handler de chat_rag del Copilot:
# 0. Reformular la query usando historial para mejorar RAG
rag_query = await rewrite_query_for_rag(message, history, chat_llm)

# 1. Buscar con la query reformulada (no con la original)
rag_context = await rag_service.get_multi_collection_context(
    query=rag_query,
    collection_names=accessible_collections,
    max_chunks=max_chunks,
)

# 2. Generar respuesta con el contexto recuperado
# (el prompt del sistema recibe la query original del usuario, no la reformulada)
