# Extraído de: LibroCISO/cap-12-agentes-especializados.md
import anthropic
from datetime import datetime, timezone

client = anthropic.Anthropic()

# Datos del tratamiento (ya obtenidos en gather_data)
processing_data = {
    "name": "Gestión de incidentes de seguridad",
    "purpose": "Registro y seguimiento de incidentes de ciberseguridad",
    "legal_basis": "Obligación legal (Art. 6.1.c RGPD) - ENS Art. 24",
    "data_categories": ["datos identificativos", "datos de conexión",
                        "logs de actividad"],
    "data_subjects": ["empleados", "usuarios del sistema"],
    "retention": "5 años (prescripción responsabilidad Art. 78 LOPDGDD)"
}

# Contexto normativo del RAG
normative_context = """
Art. 35.3 RGPD: La evaluación de impacto será obligatoria en caso de:
a) evaluación sistemática de aspectos personales basada en un
   tratamiento automatizado;
b) tratamiento a gran escala de categorías especiales de datos;
c) observación sistemática a gran escala de una zona de acceso público.

Guía AEPD: Para determinar la necesidad de DPIA, evaluar los
criterios de la lista del Art. 35.3 y el listado publicado por
la AEPD conforme al Art. 35.4.
"""

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    temperature=0.2,
    system=(
        "Eres un analista de privacidad del equipo GRC. "
        "Evalúa si el tratamiento requiere DPIA según "
        "los criterios del RGPD y de la AEPD. "
        "Cita artículos. No inventes datos."
    ),
    messages=[{
        "role": "user",
        "content": (
            f"## Tratamiento\n{processing_data}\n\n"
            f"## Normativa aplicable\n{normative_context}\n\n"
            "Genera: 1) Evaluación de necesidad de DPIA, "
            "2) Análisis de proporcionalidad, "
            "3) Riesgos identificados, "
            "4) Medidas recomendadas"
        )
    }]
)

# Registrar tracing
trace = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "model": message.model,
    "tokens_input": message.usage.input_tokens,
    "tokens_output": message.usage.output_tokens,
    "stop_reason": message.stop_reason,
    # Coste estimado (claude-sonnet-4-6 a fecha de desarrollo)
    "cost_usd": (
        message.usage.input_tokens * 3.0 / 1_000_000 +
        message.usage.output_tokens * 15.0 / 1_000_000
    )
}

print(f"Tokens: {trace['tokens_input']}+{trace['tokens_output']}")
print(f"Coste: ${trace['cost_usd']:.4f}")
print(f"Análisis:\n{message.content[0].text}")
