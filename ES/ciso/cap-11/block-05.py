# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: construcción del prompt RAG para consulta normativa
import anthropic

def build_rag_prompt(query: str, search_results: list[RAGSearchResult]) -> str:
    """Construye el prompt que combina la pregunta del usuario
    con los chunks normativos recuperados de Qdrant."""

    # Ensamblar contexto con fuentes identificadas
    context_blocks = []
    for i, result in enumerate(search_results, 1):
        source_info = f"[Fuente {i}: {result.regulation}"
        if result.article:
            source_info += f", {result.article}"
        source_info += f" — {result.document_title}]"

        context_blocks.append(f"{source_info}\n{result.text}")

    context = "\n\n---\n\n".join(context_blocks)

    return f"""Eres un asistente especializado en regulación y compliance.
Responde EXCLUSIVAMENTE basándote en el contexto normativo proporcionado.

REGLAS:
- Cita siempre la fuente específica: regulación, artículo y apartado.
- Si el contexto no contiene información suficiente para responder, dilo explícitamente.
- NO inventes artículos, apartados ni considerandos que no aparezcan en el contexto.
- Si hay ambigüedad, señálala y explica las posibles interpretaciones.
- Responde en español técnico.

CONTEXTO NORMATIVO:
{context}

PREGUNTA DEL USUARIO:
{query}"""


async def query_normative_rag(
    query: str,
    search_service: RAGSearchService,
    collection_name: str = "normative_local",
    regulation_filter: str | None = None,
) -> dict:
    """Flujo completo: pregunta → búsqueda → contexto → respuesta LLM."""

    # 1. Búsqueda semántica
    search_results = search_service.search(
        query=query,
        collection_name=collection_name,
        top_k=5,
        regulation_filter=regulation_filter,
    )

    if not search_results:
        return {
            "answer": "No se han encontrado fragmentos normativos relevantes "
                      "para esta consulta. Reformule la pregunta o amplíe "
                      "el alcance de la búsqueda.",
            "sources": [],
            "model": None,
        }

    # 2. Construir prompt con contexto
    prompt = build_rag_prompt(query, search_results)

    # 3. Llamada a Claude con el contexto normativo
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    # 4. Devolver respuesta con fuentes para trazabilidad
    return {
        "answer": response.content[0].text,
        "sources": [
            {
                "regulation": r.regulation,
                "article": r.article,
                "document": r.document_title,
                "score": round(r.score, 3),
                "source_url": r.source_url,
            }
            for r in search_results
        ],
        "model": "claude-sonnet-4-6",
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
    }
