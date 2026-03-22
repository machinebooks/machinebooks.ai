# Extraído de: LibroPQC/cap-13-rag.md
import anthropic

def build_rag_prompt(
    user_message: str,
    rag_chunks: list,
    system_base: str
) -> list:
    """
    Construir mensajes con contexto RAG inyectado.
    Los fragmentos se añaden al system prompt, no al mensaje del usuario,
    para que el modelo los trate como fuente de verdad.
    """
    # Formatear fragmentos con metadatos de origen
    context_block = "\n\n---\n\n".join([
        f"**Fuente:** {chunk['source_title']}\n"
        f"**Tipo:** {chunk.get('collection_type', 'N/A')}\n"
        f"**URL:** {chunk.get('source_url', 'N/A')}\n\n"
        f"{chunk['text']}"
        for chunk in rag_chunks
    ])

    system_prompt = (
        f"{system_base}\n\n"
        f"## Base de conocimiento (fuentes verificadas)\n\n"
        f"Usa la siguiente información como fuente primaria para "
        f"responder preguntas sobre estándares, regulaciones y "
        f"requisitos de migración PQC. Cita la fuente cuando "
        f"la uses.\n\n{context_block}"
    )

    return system_prompt, [{"role": "user", "content": user_message}]

# Ejemplo de uso en el endpoint de chat
client = anthropic.Anthropic()

rag_service = RAGSearchService()
chunks = rag_service.search(
    query="¿Qué plazos establece CNSA 2.0 para la migración?",
    collection_types=['framework', 'documentation']
)

system, messages = build_rag_prompt(
    user_message="¿Qué plazos establece CNSA 2.0 para la migración?",
    rag_chunks=chunks,
    system_base="Eres un experto en migración PQC."
)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system=system,
    messages=messages
)
