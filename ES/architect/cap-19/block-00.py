# Extraído de: LibroTecnico/cap-19-testing-ia.md
import anthropic
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class QualityProfile:
    """Perfil de calidad por categoría de servicio."""
    category: str
    hallucination_threshold: float  # máximo aceptable
    groundedness_threshold: float   # mínimo aceptable
    relevance_threshold: float
    coherence_threshold: float
    bias_threshold: float
    toxicity_threshold: float
    pii_threshold: float

# Perfiles de calidad por categoría
QUALITY_PROFILES = {
    "rag_services": QualityProfile(
        category="rag_services",
        hallucination_threshold=0.06,   # Tolerancia muy baja: <6%
        groundedness_threshold=0.85,    # Alta: >85%
        relevance_threshold=0.75,
        coherence_threshold=0.70,
        bias_threshold=0.10,
        toxicity_threshold=0.05,
        pii_threshold=0.02,             # Crítico: casi cero
    ),
    "analysis": QualityProfile(
        category="analysis",
        hallucination_threshold=0.10,
        groundedness_threshold=0.80,
        relevance_threshold=0.80,       # Alto: el análisis debe ser pertinente
        coherence_threshold=0.80,       # Alto: sin contradicciones internas
        bias_threshold=0.10,
        toxicity_threshold=0.05,
        pii_threshold=0.05,
    ),
    "generation": QualityProfile(
        category="generation",
        hallucination_threshold=0.22,   # Tolerancia moderada: hasta 22%
        groundedness_threshold=0.60,    # Menor: permite aportación creativa
        relevance_threshold=0.70,
        coherence_threshold=0.75,
        bias_threshold=0.15,
        toxicity_threshold=0.05,
        pii_threshold=0.03,
    ),
}


