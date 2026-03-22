# Extraído de: LibroCISO/cap-27-executive-dashboard.md
import anthropic

async def generate_executive_narrative(
    current_data: dict,
    previous_data: dict | None,
    organization_name: str,
    period: str,
) -> str:
    """Genera un resumen narrativo del estado GRC
    para acompañar el dashboard ejecutivo.

    Compara datos actuales con el periodo anterior
    y destaca mejoras, deterioros y áreas de atención.
    """
    client = anthropic.Anthropic()

    context = f"""Datos actuales del dashboard GRC:
{json.dumps(current_data, indent=2)}

Datos del periodo anterior:
{json.dumps(previous_data, indent=2) if previous_data else 'No disponible (primer periodo)'}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Genera un resumen ejecutivo de 3-5 párrafos
para el comité de dirección de {organization_name},
periodo {period}.

{context}

Requisitos del resumen:
- Lenguaje de dirección, no técnico
- Destacar los 3 cambios más relevantes respecto al periodo anterior
- Identificar áreas que requieren atención inmediata
- Mencionar logros y progresos
- Cerrar con recomendaciones priorizadas (máximo 3)
- Tono: profesional, directo, sin alarmismo innecesario"""
        }]
    )
    return message.content[0].text
