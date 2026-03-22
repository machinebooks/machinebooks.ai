# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Ejemplo didáctico: asistencia del agente de privacidad
# en la evaluación de una brecha — sugiere pero no decide

import anthropic


BREACH_ASSESSMENT_PROMPT = """Eres un agente experto en protección de datos
especializado en la gestión de brechas de seguridad según el RGPD.

Analiza la siguiente brecha de datos personales y proporciona:
1. Severidad recomendada (low, medium, high, critical)
2. Categorías de datos probablemente afectados
3. Si es probable que afecte a categorías especiales (Art. 9)
4. Si recomiendas notificación a la AEPD (Art. 33) y por qué
5. Si recomiendas comunicación a los interesados (Art. 34) y por qué
6. Medidas inmediatas recomendadas

REGLAS:
- Sé conservador: ante la duda, recomienda notificar.
- NUNCA digas que NO hay que notificar si hay datos de salud,
  financieros o categorías especiales implicados.
- Tu evaluación es una SUGERENCIA. El DPO decide.

BRECHA:
Título: {title}
Descripción: {description}
Afectados estimados: {affected_count}
Tipo: {breach_type}
"""


async def assess_breach_with_agent(
    title: str,
    description: str,
    affected_count: int,
    breach_type: str
) -> dict:
    """Genera una evaluación asistida por IA de la brecha.

    El resultado incluye nivel de confianza del agente.
    El DPO SIEMPRE tiene la última palabra.
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": BREACH_ASSESSMENT_PROMPT.format(
                title=title,
                description=description,
                affected_count=affected_count or "Desconocido",
                breach_type=breach_type
            )
        }]
    )

    return {
        "assessment": message.content[0].text,
        "model": "claude-sonnet-4-6",
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
        "disclaimer": (
            "Esta evaluación es una sugerencia generada por IA. "
            "La decisión de notificación corresponde al DPO según "
            "el Art. 33.1 RGPD."
        )
    }
