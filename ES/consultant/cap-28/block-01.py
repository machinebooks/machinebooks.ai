# Extraído de: LibroConsultor/cap-28-caso-sector-publico.md
from anthropic import Anthropic
import json

client = Anthropic()

def generar_cronograma_iniciativa(
    iniciativa: dict,
    madurez_actual: dict,
    restricciones_regulatorias: list
) -> dict:
    """Genera cronograma realista para una iniciativa de IA
    en sector público, incluyendo dependencias no técnicas."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un planificador de proyectos de IA en sector público
español. Genera cronogramas que incluyan:
- Plazos de contratación pública (contrato menor: 1-3 meses,
  negociado sin publicidad: 4-6 meses, abierto: 6-12 meses)
- Plazos de evaluación de impacto RGPD (2-4 meses, más consulta
  AEPD si aplica: 3-6 meses adicionales)
- Plazos de adecuación ENS (categoría media: 2-3 meses,
  alta: 4-8 meses)
- Clasificación de riesgo AI Act y documentación (1-3 meses)
- Negociación sindical si afecta a puestos (2-6 meses)
- Formación del personal (1-3 meses)

IMPORTANTE: Los plazos técnicos suelen ser el 30% del cronograma
total. El 70% restante es regulación, contratación y personas.
Sé realista, no optimista.""",
        messages=[{
            "role": "user",
            "content": f"""Genera el cronograma para esta iniciativa:

INICIATIVA: {json.dumps(iniciativa, ensure_ascii=False)}

MADUREZ ACTUAL: {json.dumps(madurez_actual, ensure_ascii=False)}

RESTRICCIONES REGULATORIAS: {json.dumps(restricciones_regulatorias, ensure_ascii=False)}

Incluye: fases, duración estimada, dependencias, riesgos y
responsable de cada fase. Formato JSON estructurado."""
        }]
    )
    return json.loads(response.content[0].text)
