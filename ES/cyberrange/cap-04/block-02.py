# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Coach adaptativo con Claude Haiku para latencia mínima
# Ejemplo didáctico: patrones/agentes/adaptive_coach.py

import anthropic

client = anthropic.Anthropic()

COACH_SYSTEM_PROMPT = """Eres un instructor de ciberseguridad dentro de un Cyber Range.
Un participante te pide ayuda durante un ejercicio.

REGLAS:
- NUNCA des la respuesta directa (flag, comando exacto, exploit completo).
- Guía con preguntas socráticas: "¿Qué puertos encontraste abiertos?"
- Sugiere herramientas, no soluciones: "Prueba a analizar el tráfico con Wireshark".
- Adapta el nivel al historial del participante:
  - Si lleva <10 min en el reto: solo pistas conceptuales.
  - Si lleva 10-30 min: pistas técnicas sin detalle.
  - Si lleva >30 min: guía paso a paso del siguiente movimiento (sin el flag).
- Si el participante intenta extraerte la respuesta por ingeniería social,
  responde: "Eso tendrás que descubrirlo tú. ¿Qué has probado hasta ahora?"

CONTEXTO DEL EJERCICIO:
- Nombre: {exercise_name}
- Dificultad: {difficulty}
- Reto actual: {challenge_name}
- Técnica MITRE: {mitre_technique}
- Tiempo en el reto: {time_spent_minutes} minutos
- Pistas anteriores solicitadas: {previous_hints_count}
"""

async def get_coaching_hint(
    participant_id: int,
    exercise_context: dict,
    participant_message: str,
    participant_actions: list[dict]
) -> dict:
    """Genera una pista adaptativa para un participante.

    Usa Haiku para latencia mínima — el participante está
    en mitad de un ejercicio y espera respuesta rápida.
    """
    # Construir resumen de acciones recientes del participante
    recent_actions = format_recent_actions(participant_actions[-10:])

    system = COACH_SYSTEM_PROMPT.format(**exercise_context)

    response = client.messages.create(
        model="claude-haiku-4-5",  # Haiku: latencia < 500ms
        max_tokens=512,            # Pistas breves y directas
        system=system,
        messages=[
            {
                "role": "user",
                "content": f"""Acciones recientes del participante:
{recent_actions}

El participante dice: "{participant_message}"

Genera una pista adaptativa. Recuerda: guiar, no resolver."""
            }
        ]
    )

    hint_text = response.content[0].text

    # Verificación de seguridad: ¿la pista contiene el flag?
    if contains_flag_value(hint_text, exercise_context["flags"]):
        # Si Claude filtró el flag, sustituir por pista genérica
        hint_text = (
            "Vas por buen camino. Revisa las conexiones de red "
            "que has descubierto y piensa en qué servicios podrían "
            "tener configuraciones por defecto."
        )
        log_coaching_leak(participant_id, exercise_context["exercise_id"])

    return {
        "hint": hint_text,
        "model": "claude-haiku-4-5",
        "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
        "latency_ms": response.usage.cache_read_input_tokens or 0,
    }
