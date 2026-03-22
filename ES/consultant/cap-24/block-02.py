# Extraído de: LibroConsultor/cap-24-cuando-no-usar-ia.md
from datetime import date, timedelta
from dataclasses import dataclass

@dataclass
class DigitalFastingPolicy:
    """Política de ayuno digital para mantener habilidades base.

    Cada consultor dedica tiempo regulado a trabajo sin asistencia IA
    para preservar capacidad de análisis y redacción autónomos."""

    # Un día al mes sin herramientas de IA para tareas analíticas
    monthly_fast_day: int = 15  # Día del mes

    # Cada propuesta nueva: primer borrador de enfoque SIN IA
    proposal_first_draft_manual: bool = True

    # Reuniones de diagnóstico con cliente: sin preparación IA
    diagnostic_meetings_manual: bool = True

    # Revisión de entregables: al menos una revisión sin sugerencias IA
    final_review_manual: bool = True

    def should_use_ai(self, task_type: str, current_date: date) -> dict:
        """Determina si una tarea debe realizarse con o sin IA."""
        is_fast_day = current_date.day == self.monthly_fast_day

        rules = {
            "proposal_approach": {
                "ai_allowed": not self.proposal_first_draft_manual,
                "reason": "El primer borrador estratégico ejercita "
                         "el pensamiento independiente del consultor"
            },
            "client_diagnostic": {
                "ai_allowed": not self.diagnostic_meetings_manual,
                "reason": "La lectura de la sala y la escucha activa "
                         "requieren presencia humana completa"
            },
            "deliverable_review": {
                "ai_allowed": not self.final_review_manual,
                "reason": "La revisión final debe aplicar criterio "
                         "humano sin sesgo de confirmación del modelo"
            },
            "routine_analysis": {
                "ai_allowed": not is_fast_day,
                "reason": "Día de ayuno digital: tareas analíticas "
                         "sin asistencia IA" if is_fast_day else "OK"
            }
        }

        return rules.get(task_type, {
            "ai_allowed": not is_fast_day,
            "reason": "Política general"
        })
