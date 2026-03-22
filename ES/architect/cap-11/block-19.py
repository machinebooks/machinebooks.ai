# Extraído de: LibroTecnico/cap-11-integracion-llms.md
import json
from pydantic import BaseModel, ValidationError

# Schema de respuesta esperada
class DocumentAnalysisResult(BaseModel):
    summary: str
    requirements: list[str]
    go_no_go: str  # "GO" | "NO_GO" | "CONDITIONAL"
    confidence: float
    risk_factors: list[str]

# Instrucción de formato en el prompt
FORMAT_INSTRUCTION = """
Responde EXCLUSIVAMENTE con un objeto JSON válido con esta estructura:
{
  "summary": "resumen ejecutivo en máximo 300 palabras",
  "requirements": ["req1", "req2", ...],
  "go_no_go": "GO | NO_GO | CONDITIONAL",
  "confidence": 0.0-1.0,
  "risk_factors": ["riesgo1", "riesgo2", ...]
}
No incluyas texto antes ni después del JSON. No uses bloques de código markdown.
"""

def parse_llm_response(raw_response: str, schema: type[BaseModel]) -> BaseModel:
    """Parsea y valida la respuesta del modelo contra un schema Pydantic."""
    # Limpiar posibles artefactos de formato
    cleaned = raw_response.strip()
    if cleaned.startswith("