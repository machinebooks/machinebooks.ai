# Extraído de: LibroConsultor/cap-18-onboarding.md
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class JuniorProgress:
    """Seguimiento del progreso de un junior en el programa."""
    junior_id: str
    name: str
    start_date: str
    assigned_project_type: str           # "audit_security", "architecture", "ai_adoption"
    current_phase: str = "immersion"     # "immersion", "simulation", "assisted_production"
    current_week: int = 1

    # Métricas de inmersión (fase 1)
    docs_read: list[str] = field(default_factory=list)
    mentor_queries: int = 0
    mentor_gaps_triggered: int = 0       # Preguntas sin respuesta en el RAG
    quiz_scores: list[float] = field(default_factory=list)

    # Métricas de simulación (fase 2)
    scenarios_completed: list[dict] = field(default_factory=list)
    avg_scenario_score: float = 0.0
    common_weaknesses: list[str] = field(default_factory=list)

    # Métricas de producción (fase 3)
    deliverables_produced: int = 0
    deliverables_approved: int = 0
    revision_rounds_avg: float = 0.0     # Media de rondas de revisión por deliverable
    first_billable_date: Optional[str] = None

    def days_to_first_billable(self) -> Optional[int]:
        """Calcula días desde inicio hasta primera entrega facturable."""
        if not self.first_billable_date:
            return None
        start = datetime.fromisoformat(self.start_date)
        billable = datetime.fromisoformat(self.first_billable_date)
        return (billable - start).days

    def ready_for_next_phase(self) -> bool:
        """Evalúa si el junior puede avanzar a la siguiente fase."""
        if self.current_phase == "immersion":
            return (len(self.quiz_scores) >= 1
                    and self.quiz_scores[-1] >= 0.8)
        elif self.current_phase == "simulation":
            acceptable = [s for s in self.scenarios_completed
                         if s.get("rating") in ("excelente", "aceptable")]
            return len(acceptable) >= 3
        return False

def generate_weekly_report(progress: JuniorProgress) -> dict:
    """Genera informe semanal de progreso para el mentor humano."""
    report_prompt = f"""Genera un informe de progreso semanal para el mentor
de un consultor junior en programa de onboarding.

Datos del junior:
- Semana: {progress.current_week}
- Fase: {progress.current_phase}
- Proyecto asignado: {progress.assigned_project_type}
- Documentos leídos: {len(progress.docs_read)}
- Consultas al mentor IA: {progress.mentor_queries}
- Lagunas detectadas: {progress.mentor_gaps_triggered}
- Última puntuación de quiz: {progress.quiz_scores[-1] if progress.quiz_scores else 'N/A'}
- Escenarios completados: {len(progress.scenarios_completed)}
- Puntuación media escenarios: {progress.avg_scenario_score:.1f}
- Debilidades recurrentes: {', '.join(progress.common_weaknesses) or 'Ninguna detectada'}

Genera:
1. Resumen de progreso en 3-4 líneas
2. Áreas donde el junior progresa bien (máximo 3)
3. Áreas que requieren atención del mentor humano (máximo 3)
4. Recomendación: ¿listo para avanzar de fase? Sí/No con justificación
5. Sugerencia de actividades para la próxima semana
"""

    response = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para informes rutinarios, menor coste
        max_tokens=1024,
        system="Eres un coordinador de programas de formación. "
               "Tus informes son concisos, factuales y orientados a acción.",
        messages=[{"role": "user", "content": report_prompt}]
    )

    return {
        "junior_id": progress.junior_id,
        "week": progress.current_week,
        "report": response.content[0].text,
        "phase_transition_recommended": progress.ready_for_next_phase()
    }
