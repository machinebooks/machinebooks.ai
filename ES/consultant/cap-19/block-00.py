# Extraído de: LibroConsultor/cap-19-lecciones-aprendidas.md
import anthropic
from dataclasses import dataclass, field
from enum import Enum
from datetime import date

class LessonPolarity(Enum):
    POSITIVE = "positive"    # Qué funcionó bien
    NEGATIVE = "negative"    # Qué falló o se podría mejorar
    NEUTRAL = "neutral"      # Cambio de contexto sin valoración

class ImpactArea(Enum):
    COST = "cost"
    SCHEDULE = "schedule"
    QUALITY = "quality"
    CLIENT_SATISFACTION = "client_satisfaction"
    TEAM = "team"

@dataclass
class LessonCandidate:
    """Lección candidata extraída de documentos de proyecto."""
    summary: str                    # Resumen en 1-2 frases
    context: str                    # Situación completa que originó la lección
    what_happened: str              # Qué ocurrió exactamente
    root_cause: str                 # Causa raíz identificada (o hipótesis)
    recommendation: str             # Qué hacer distinto en el futuro
    project_type: str               # Tipo de proyecto (auditoría, migración...)
    project_phase: str              # Fase donde ocurrió
    category: str                   # Categoría de la lección
    impact_areas: list[ImpactArea]  # Áreas de impacto
    polarity: LessonPolarity        # Positiva, negativa o neutral
    confidence: float               # Confianza del agente (0.0-1.0)
    source_documents: list[str]     # Documentos de origen
    extraction_date: date = field(default_factory=date.today)
