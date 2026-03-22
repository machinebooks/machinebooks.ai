# Extraído de: LibroCISO/cap-04-registro-tratamientos.md
# Ejemplo didáctico: agente de privacidad que interpreta una descripción
# y genera un borrador de tratamiento conforme al Art. 30.1 RGPD
# Basado en Claude Agent SDK

import anthropic
import json

PRIVACY_AGENT_SYSTEM = """Eres un agente experto en protección de datos personales,
especializado en el RGPD (Reglamento UE 2016/679) y la LOPDGDD (LO 3/2018).

Tu tarea es analizar la descripción de un tratamiento de datos personales
y generar un borrador de registro de actividad de tratamiento conforme
al Art. 30.1 del RGPD.

Para cada tratamiento, debes identificar:
1. Finalidades del tratamiento (Art. 30.1.b)
2. Base jurídica más apropiada (Art. 6.1 RGPD) — usa SOLO una de:
   consent, contract, legal_obligation, vital_interest,
   public_interest, legitimate_interest
3. Categorías de interesados y de datos personales (Art. 30.1.c)
4. Si hay categorías especiales del Art. 9 (salud, biométricos, etc.)
5. Destinatarios previstos (Art. 30.1.d)
6. Si hay transferencias internacionales (Art. 30.1.e)
7. Plazos de conservación recomendados (Art. 30.1.f)
8. Medidas de seguridad recomendadas (Art. 30.1.g, Art. 32)
9. Si requiere DPIA (Art. 35)

REGLAS:
- Responde SIEMPRE en JSON válido con la estructura solicitada.
- Si no tienes información suficiente para un campo, indica "requiere_confirmacion".
- Para la base jurídica, elige la más probable pero SIEMPRE indica tu nivel
  de confianza (alta/media/baja) — el DPO debe validar esta decisión.
- Si detectas posibles categorías especiales (Art. 9), márcalo como
  "dpia_required": true y explica por qué.
- NO inventes datos. Si la descripción no menciona transferencias
  internacionales, pon "international_transfers": false.
"""

GENERATION_PROMPT = """Analiza esta descripción de un tratamiento de datos
y genera un borrador de registro conforme al Art. 30.1 RGPD:

DESCRIPCIÓN DEL TRATAMIENTO:
{description}

CONTEXTO DE LA ORGANIZACIÓN:
- Sector: {sector}
- Tamaño: {size}

Genera el JSON estructurado del borrador."""


async def generate_processing_activity_draft(
    description: str,
    sector: str = "general",
    size: str = "mediana"
) -> dict:
    """Genera un borrador de tratamiento desde una descripción libre.

    El agente interpreta la descripción y mapea cada elemento
    a los campos del Art. 30.1. El DPO debe revisar el resultado.
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=PRIVACY_AGENT_SYSTEM,
        messages=[{
            "role": "user",
            "content": GENERATION_PROMPT.format(
                description=description,
                sector=sector,
                size=size
            )
        }]
    )

    # Parsear respuesta JSON del agente
    response_text = message.content[0].text
    draft = json.loads(response_text)

    # Marcar campos que requieren confirmación del DPO
    draft["_metadata"] = {
        "generated_by": "privacy_agent",
        "model": "claude-sonnet-4-6",
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
        "requires_dpo_review": True,
        "confidence": draft.get("legal_basis_confidence", "media")
    }

    return draft
