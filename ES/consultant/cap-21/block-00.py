# Extraído de: LibroConsultor/cap-21-productizacion.md
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class MaturityLevel(Enum):
    AD_HOC = 1       # Sin procesos definidos
    EXPERIMENTAL = 2  # Pilotos aislados
    OPERATIONAL = 3   # IA en producción, casos puntuales
    OPTIMIZED = 4     # IA integrada, métricas, gobernanza
    TRANSFORMATIVE = 5 # IA como ventaja competitiva sistémica

@dataclass
class DimensionScore:
    dimension: str          # "datos", "talento", "gobernanza", etc.
    score: float            # 1.0 a 5.0
    confidence: float       # 0.0 a 1.0 — baja si hay inconsistencias
    inconsistencies: list   # Respuestas contradictorias detectadas
    evidence_gaps: list     # Evidencias que faltan para validar

@dataclass
class AssessmentResult:
    client_id: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    overall_level: MaturityLevel = MaturityLevel.AD_HOC
    flags_for_consultant: list[str] = field(default_factory=list)

    def calculate_overall(self):
        """Nivel global = media ponderada, penalizada por inconsistencias."""
        if not self.dimensions:
            return
        weighted_sum = sum(
            d.score * d.confidence for d in self.dimensions
        )
        total_confidence = sum(d.confidence for d in self.dimensions)
        avg = weighted_sum / total_confidence if total_confidence > 0 else 1.0
        self.overall_level = MaturityLevel(min(5, max(1, round(avg))))

        # Marcar dimensiones con baja confianza para revisión humana
        for d in self.dimensions:
            if d.confidence < 0.6:
                self.flags_for_consultant.append(
                    f"Dimensión '{d.dimension}': confianza {d.confidence:.0%}. "
                    f"Inconsistencias: {', '.join(d.inconsistencies[:3])}"
                )
