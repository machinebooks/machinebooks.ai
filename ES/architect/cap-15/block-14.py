# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
# Ejemplo didáctico: patrones/chat/history_manager.py

def estimate_tokens(text: str) -> int:
    # Claude usa un tokenizador propio; tiktoken (OpenAI) daría conteos incorrectos.
    # Aproximación práctica: 1 token ≈ 4 caracteres en español.
    return len(text) // 4

def manage_history(messages: list[dict], budget: int) -> list[dict]:
    """Gestiona el historial de conversación dentro del presupuesto."""
    total_tokens = sum(estimate_tokens(m["content"]) for m in messages)

    if total_tokens <= budget:
        return messages  # Cabe completo, no truncar

    # Conservar primer mensaje + últimos N mensajes
    first_message = messages[0]
    recent_window = 6  # Últimos 3 turnos (user + assistant)

    if len(messages) <= recent_window + 1:
        return messages  # Muy pocos mensajes, no comprimir

    middle_messages = messages[1:-recent_window]

    # Generar resumen de los mensajes intermedios con Haiku
    summary = compress_to_summary(middle_messages)

    return [
        first_message,
        {"role": "user", "content": f"[Resumen de la conversación anterior: {summary}]"},
        {"role": "assistant", "content": "Entendido, continúo con ese contexto."},
        *messages[-recent_window:]
    ]
