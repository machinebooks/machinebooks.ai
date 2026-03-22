# Extraído de: LibroConsultor/cap-15-madurez-ia.md
from dataclasses import dataclass

@dataclass
class DimensionScore:
    dimension: Dimension
    level: float          # 1.0 - 5.0, con decimales
    confidence: float     # 0.0 - 1.0
    evidence_ratio: float # Proporción de respuestas con evidencia
    key_findings: list[str]
    gaps: list[str]
    strengths: list[str]

@dataclass
class MaturityAssessment:
    organization: str
    sector: str
    size_band: str          # "200-500", "500-2000", "2000+"
    assessment_date: str
    dimensions: list[DimensionScore]
    overall_level: float
    stakeholders_interviewed: int

    @property
    def overall_level_weighted(self) -> float:
        """Nivel global ponderado — datos y personas pesan más."""
        weights = {
            Dimension.STRATEGY: 0.15,
            Dimension.DATA: 0.25,      # Peso mayor: sin datos no hay IA
            Dimension.TECHNOLOGY: 0.20,
            Dimension.PEOPLE: 0.25,    # Peso mayor: sin personas no hay cambio
            Dimension.GOVERNANCE: 0.15,
        }
        total = sum(
            d.level * weights[d.dimension] for d in self.dimensions
        )
        return round(total, 1)


def score_dimension(
    dimension: Dimension,
    interview_responses: list[dict],
    evidence_docs: list[str],
    objective_indicators: dict
) -> DimensionScore:
    """Puntúa una dimensión combinando entrevistas, evidencia e indicadores."""

    scoring_prompt = f"""Evalúa la madurez en la dimensión '{dimension.value}'
con base en las siguientes fuentes:

## Respuestas de entrevistas
{_format_responses(interview_responses)}

## Evidencia documental recogida
{chr(10).join(f"- {doc}" for doc in evidence_docs) or "Ninguna"}

## Indicadores objetivos
{_format_indicators(objective_indicators)}

## Escala de evaluación (dimensión: {dimension.value})
- Nivel 1 (Ad-hoc): {LEVEL_DESCRIPTORS[dimension][1]}
- Nivel 2 (Experimental): {LEVEL_DESCRIPTORS[dimension][2]}
- Nivel 3 (Operativo): {LEVEL_DESCRIPTORS[dimension][3]}
- Nivel 4 (Optimizado): {LEVEL_DESCRIPTORS[dimension][4]}
- Nivel 5 (Transformador): {LEVEL_DESCRIPTORS[dimension][5]}

Instrucciones:
- Asigna un nivel con un decimal (ej: 2.3)
- Indica tu confianza (0.0-1.0) basada en la calidad de la evidencia
- Si las respuestas son solo declarativas sin evidencia, reduce confianza
- Lista hallazgos principales, gaps y fortalezas
- Sé conservador: ante la duda, puntúa a la baja

Responde en JSON con: level, confidence, evidence_ratio,
key_findings, gaps, strengths"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": scoring_prompt}]
    )

    # Parsear respuesta JSON y construir DimensionScore
    result = _parse_scoring_response(response.content[0].text)
    return DimensionScore(dimension=dimension, **result)
