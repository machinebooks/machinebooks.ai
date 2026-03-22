# Extraído de: LibroConsultor/cap-17-memoria-institucional.md
# proactive/context_alerts.py — Alertas proactivas de conocimiento
from dataclasses import dataclass

@dataclass
class ProjectContext:
    """Contexto del proyecto actual para alertas proactivas."""
    sector: str
    dominio: list[str]
    tipo_proyecto: str
    tecnologias: list[str]
    descripcion_breve: str

def generate_proactive_alerts(
    project: ProjectContext,
    knowledge_store,
    max_alerts: int = 5
) -> list[dict]:
    """Genera alertas proactivas basadas en el contexto del proyecto."""
    alerts = []

    # Buscar lecciones aprendidas en proyectos similares
    lessons = knowledge_store.search_knowledge(
        query=project.descripcion_breve,
        query_embedding=generate_embedding(project.descripcion_breve),
        filters={
            "sector": [project.sector],
            "dominio": project.dominio,
            "relevancia_min": 4  # Solo fragmentos de alta relevancia
        },
        top_k=max_alerts
    )

    # Filtrar por tipo: priorizamos lecciones y decisiones sobre insights
    priority_order = {"lesson": 0, "decision": 1, "pattern": 2, "insight": 3}
    lessons.sort(key=lambda x: priority_order.get(x["type"], 99))

    for lesson in lessons[:max_alerts]:
        alerts.append({
            "type": lesson["type"],
            "summary": lesson["content"][:200] + "...",
            "full_content": lesson["content"],
            "relevance_score": lesson["score"],
            "action": _suggest_action(lesson)
        })

    return alerts

def _suggest_action(fragment: dict) -> str:
    """Sugiere una acción basada en el tipo de fragmento."""
    actions = {
        "lesson": "Revisa esta lección antes de repetir el enfoque.",
        "decision": "Considera esta decisión como precedente.",
        "pattern": "Este patrón se observó en proyectos similares.",
        "insight": "Información de contexto que puede ser relevante."
    }
    return actions.get(fragment["type"], "Fragmento relevante encontrado.")
