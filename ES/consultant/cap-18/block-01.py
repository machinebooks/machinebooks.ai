# Extraído de: LibroConsultor/cap-18-onboarding.md
import anthropic
from qdrant_client import QdrantClient

# Conexión al RAG de onboarding
qdrant = QdrantClient(url="http://localhost:6333")
client = anthropic.Anthropic(api_key="<TU_ANTHROPIC_KEY>")

MENTOR_SYSTEM_PROMPT = """Eres un mentor de consultoría tecnológica. Tu rol es ayudar
a consultores junior a entender las metodologías, estándares y prácticas de la consultoría.

Reglas:
1. Responde SOLO con información del contexto proporcionado (documentos de la práctica).
2. Si no tienes información suficiente, di "No tengo documentación sobre esto —
   pregunta a tu mentor asignado" y registra la laguna.
3. Cuando cites un procedimiento, indica el documento fuente para que el junior
   pueda leerlo completo.
4. Adapta la profundidad de la respuesta al nivel del junior (foundational,
   intermediate, advanced).
5. Después de responder, sugiere 1-2 documentos relacionados que amplíen el tema.
6. NUNCA inventes procedimientos ni estándares. Si algo no está documentado,
   es una laguna que debe escalarse.
7. Incluye ejemplos concretos cuando sea posible.

Nivel del junior: {difficulty_level}
Semana de onboarding: {onboarding_week}
Proyecto asignado: {assigned_project_type}
"""

def query_mentor(
    question: str,
    junior_profile: dict,
    collection: str = "onboarding_docs"
) -> dict:
    """Consulta al agente de mentoría con contexto RAG."""
    # Buscar documentos relevantes en el índice de onboarding
    search_results = qdrant.search(
        collection_name=collection,
        query_vector=get_embedding(question),
        query_filter={
            "must": [
                {"key": "difficulty",
                 "range": {"lte": junior_profile["current_level"]}}
            ]
        },
        limit=5
    )

    # Construir contexto con los documentos recuperados
    context_docs = "\n\n---\n\n".join([
        f"[{r.payload['title']}] (Categoría: {r.payload['category']}, "
        f"Nivel: {r.payload['difficulty']})\n{r.payload['content']}"
        for r in search_results
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=MENTOR_SYSTEM_PROMPT.format(
            difficulty_level=junior_profile["current_level"],
            onboarding_week=junior_profile["week"],
            assigned_project_type=junior_profile["project_type"]
        ),
        messages=[{
            "role": "user",
            "content": f"Contexto de la práctica:\n{context_docs}\n\n"
                       f"Pregunta del junior:\n{question}"
        }]
    )

    return {
        "answer": response.content[0].text,
        "sources": [r.payload["title"] for r in search_results],
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        "gap_detected": "No tengo documentación" in response.content[0].text
    }
