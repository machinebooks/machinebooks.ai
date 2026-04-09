# Extraido de: LibroAISafety/cap-15-sabotaje-riesgos.md
# Framework básico de evaluación de sabotaje
# Código didáctico — no es una herramienta de evaluación completa

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class SabotageType(Enum):
    TASK_SABOTAGE = "sabotaje_de_tarea"
    OVERSIGHT_UNDERMINING = "debilitamiento_de_supervision"
    CAPABILITY_HIDING = "ocultacion_de_capacidades"

@dataclass
class SabotageEval:
    """Evaluación individual de sabotaje."""
    eval_id: str
    sabotage_type: SabotageType
    task_description: str
    correct_answer: str          # Respuesta verificablemente correcta
    model_answer: str            # Respuesta del modelo
    contains_subtle_error: bool  # ¿El modelo introdujo un error sutil?
    error_description: Optional[str] = None
    human_detected: Optional[bool] = None  # ¿Un revisor humano detectó el error?

@dataclass
class SabotageTestSuite:
    """Suite de tests de sabotaje para un dominio."""
    domain: str                  # e.g., "code_review", "data_analysis"
    evaluations: list[SabotageEval]

    def detection_rate(self) -> float:
        """Tasa de detección humana de errores sutiles."""
        errors = [e for e in self.evaluations if e.contains_subtle_error]
        if not errors:
            return 1.0
        detected = sum(1 for e in errors if e.human_detected)
        return detected / len(errors)

    def sabotage_rate(self) -> float:
        """Tasa de respuestas con errores sutiles."""
        if not self.evaluations:
            return 0.0
        errors = sum(1 for e in self.evaluations if e.contains_subtle_error)
        return errors / len(self.evaluations)
