# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# query/knowledge_search.py — Interfaz de búsqueda para consultores
import anthropic
import json

client = anthropic.Anthropic()

QUERY_ANALYSIS_PROMPT = """Analiza la consulta del usuario y extrae:
1. intent: qué busca (precedente, patrón, decisión, lección, tecnología)
2. filters: filtros implícitos (sector, dominio, tipo de proyecto)
3. refined_query: la consulta reformulada para búsqueda semántica

Devuelve JSON: {"intent": "...", "filters": {...}, "refined_query": "..."}"""

SYNTHESIS_PROMPT = """Eres el asistente de conocimiento de una práctica
de consultoría. El usuario ha hecho una consulta y estos son los
fragmentos más relevantes de la base de conocimiento.

Responde de forma útil:
- Resume los hallazgos más relevantes
- Indica de qué proyecto/contexto proviene cada dato
- Si hay contradicciones entre fragmentos, señálalas
- Si la evidencia es escasa, dilo explícitamente
- Nunca inventes información que no esté en los fragmentos"""

def search_and_synthesize(user_query: str, project_context: dict = None) -> str:
    """Busca conocimiento relevante y sintetiza una respuesta."""
    # Paso 1: Analizar la consulta para extraer filtros implícitos
    analysis = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        messages=[{"role": "user", "content": user_query}],
        system=QUERY_ANALYSIS_PROMPT,
        temperature=0.0
    )
    parsed = json.loads(analysis.content[0].text)

    # Paso 2: Generar embedding de la consulta refinada
    query_embedding = generate_embedding(parsed["refined_query"])

    # Paso 3: Buscar en Qdrant con filtros extraídos
    from storage.knowledge_store import search_knowledge
    results = search_knowledge(
        query=parsed["refined_query"],
        query_embedding=query_embedding,
        filters=parsed.get("filters"),
        top_k=8
    )

    if not results:
        return ("No encontré precedentes relevantes en la base de "
                "conocimiento. Considera consultar directamente con "
                "el equipo senior.")

    # Paso 4: Sintetizar respuesta con contexto
    context = "\n\n".join([
        f"**Fragmento {i+1}** (tipo: {r['type']}, "
        f"sector: {r.get('sector', 'N/A')}, "
        f"relevancia: {r.get('relevancia', 'N/A')}/5):\n{r['content']}"
        for i, r in enumerate(results)
    ])

    synthesis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Consulta: {user_query}\n\nFragmentos:\n{context}"
        }],
        system=SYNTHESIS_PROMPT,
        temperature=0.2
    )

    return synthesis.content[0].text
