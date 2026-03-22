# Extraído de: LibroConsultor/cap-24-cuando-no-usar-ia.md
from anthropic import Anthropic
from dataclasses import dataclass
from enum import Enum

class VerifiabilityLevel(Enum):
    FACTUAL = "factual"          # Dato verificable: artículo, fecha, cifra
    ANALYTICAL = "analytical"     # Conclusión derivada de datos
    JUDGMENTAL = "judgmental"      # Juicio que requiere contexto humano
    SPECULATIVE = "speculative"   # Predicción o extrapolación

@dataclass
class Claim:
    text: str
    level: VerifiabilityLevel
    source_required: bool
    verified: bool = False

def classify_claims(document_text: str) -> list[Claim]:
    """Extrae y clasifica afirmaciones de un documento generado con IA.

    Las afirmaciones FACTUAL requieren verificación obligatoria.
    Las JUDGMENTAL requieren revisión por un senior del dominio.
    Las SPECULATIVE se marcan para decisión editorial."""

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Analiza el texto y extrae cada afirmación clasificándola:
        - FACTUAL: referencias normativas, estadísticas, fechas, nombres
        - ANALYTICAL: conclusiones derivadas de datos presentados
        - JUDGMENTAL: valoraciones que dependen de contexto no documentado
        - SPECULATIVE: predicciones o extrapolaciones sin base empírica
        Devuelve JSON con: text, level, source_required (true si FACTUAL)""",
        messages=[{"role": "user", "content": document_text}]
    )

    # Parsear respuesta y construir lista de claims
    # Las afirmaciones FACTUAL entran en cola de verificación manual
    # Las JUDGMENTAL se escalan al senior del proyecto
    return parse_claims(response.content[0].text)
