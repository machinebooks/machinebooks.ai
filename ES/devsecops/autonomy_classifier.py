# Extraído de: LibroDevSecOps/cap-29-futuro-seguridad-autonoma.md
# autonomy_classifier.py — Clasifica hallazgos por nivel de autonomía
from dataclasses import dataclass
from enum import IntEnum
import anthropic

class AutonomyLevel(IntEnum):
    AUTONOMOUS = 1      # Agente actúa sin aprobación
    SUPERVISED = 2      # Agente propone, humano aprueba
    HUMAN_ONLY = 3      # Humano decide y ejecuta

@dataclass
class Finding:
    severity: str           # critical, high, medium, low
    category: str           # dependency, code, secret, config, runtime
    reversible: bool        # ¿se puede deshacer?
    affects_production: bool
    component_criticality: str  # core, standard, peripheral

def classify_autonomy(finding: Finding) -> AutonomyLevel:
    """Clasifica un hallazgo en nivel de autonomía basado en políticas."""
    # Nivel 3: siempre humano para hallazgos en componentes core
    # con impacto en producción e irreversibles
    if (finding.component_criticality == "core"
        and finding.affects_production
        and not finding.reversible):
        return AutonomyLevel.HUMAN_ONLY

    # Nivel 1: autónomo para dependencias reversibles no críticas
    if (finding.category == "dependency"
        and finding.reversible
        and finding.severity in ("medium", "low")
        and finding.component_criticality != "core"):
        return AutonomyLevel.AUTONOMOUS

    # Nivel 1: secretos en pre-commit siempre autónomo (bloquear)
    if finding.category == "secret" and not finding.affects_production:
        return AutonomyLevel.AUTONOMOUS

    # Nivel 2: todo lo demás requiere supervisión
    return AutonomyLevel.SUPERVISED
