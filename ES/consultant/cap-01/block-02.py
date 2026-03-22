# Extraído de: LibroConsultor/cap-01-crisis-consultoria.md
from claude_code_sdk import Agent, tool

@tool
def search_past_proposals(sector: str, framework: str, limit: int = 5) -> list[dict]:
    """Busca propuestas anteriores en sectores y marcos similares."""
    results = search_relevant_experience(
        query=f"propuesta {sector} {framework}",
        filters={"sector": sector, "resultado": "ganada"},
        limit=limit
    )
    return [{"text": r.payload["text"], "score": r.score} for r in results]

@tool
def search_lessons_learned(topic: str, limit: int = 5) -> list[dict]:
    """Busca lecciones aprendidas relevantes para un tema."""
    results = search_relevant_experience(
        query=topic,
        filters={"doc_type": "leccion"},
        limit=limit
    )
    return [{"text": r.payload["text"], "fecha": r.payload.get("fecha")} for r in results]

@tool
def estimate_effort(project_type: str, scope_description: str) -> dict:
    """Estima esfuerzo basándose en proyectos históricos similares."""
    # Buscar proyectos similares completados
    similar = search_relevant_experience(
        query=f"{project_type}: {scope_description}",
        filters={"doc_type": "proyecto_completado"},
        limit=10
    )
    # Extraer métricas de esfuerzo de proyectos similares
    efforts = extract_effort_metrics(similar)
    return {
        "media_horas": sum(e["horas"] for e in efforts) / len(efforts),
        "rango": [min(e["horas"] for e in efforts), max(e["horas"] for e in efforts)],
        "proyectos_referencia": len(efforts),
        "confianza": "alta" if len(efforts) >= 5 else "media" if len(efforts) >= 3 else "baja"
    }

# Configurar el agente con las herramientas disponibles
rfp_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[search_past_proposals, search_lessons_learned, estimate_effort],
    system_prompt="""Eres un analista senior de consultoría. Tu trabajo es:
1. Analizar el RFP proporcionado
2. Buscar experiencia previa relevante en la base de conocimiento
3. Identificar lecciones aprendidas aplicables
4. Estimar el esfuerzo basándote en proyectos históricos
5. Emitir una recomendación go/no-go con justificación cuantitativa

Sé honesto sobre la confianza de tu análisis. Si no hay suficientes
datos históricos para una estimación fiable, dilo explícitamente."""
)
