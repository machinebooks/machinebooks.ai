# Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
# Ejemplo didáctico: Coaching IA en tiempo real
import anthropic

async def deliver_coaching_hint(
    session_id: str,
    player_context: dict,
    challenge_info: dict
):
    """Generar y entregar pista de coaching por WebSocket"""
    client = anthropic.Anthropic()

    # Generar pista contextualizada con Claude
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=(
            "Eres un instructor de ciberseguridad. "
            "Genera una pista breve y progresiva para el "
            "jugador, sin revelar la solución directamente. "
            "Adapta el nivel de detalle según los intentos previos."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Desafío: {challenge_info['description']}\n"
                f"Técnica MITRE: {challenge_info['mitre_technique']}\n"
                f"Intentos del jugador: {player_context['attempts']}\n"
                f"Último comando: {player_context['last_command']}\n"
                f"Tiempo en el desafío: {player_context['elapsed_min']} min"
            )
        }]
    )

    hint_text = message.content[0].text

    # Entregar la pista inmediatamente por WebSocket
    await websocket_manager.send_to_session(session_id, {
        "type": "coaching_hint",
        "hint": hint_text,
        "hint_level": player_context["attempts"],
        "mitre_technique": challenge_info["mitre_technique"],
        "source": "ai_coach"
    })
