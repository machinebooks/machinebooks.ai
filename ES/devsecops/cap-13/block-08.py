# Extraído de: LibroDevSecOps/cap-13-prompt-injection.md
def invoke_claude_with_safety(
    user_input: str,
    system_prompt: str,
    messages: list[dict]
) -> dict:
    """Invocación de Claude con registro de seguridad."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=messages,
    )

    # Claude indica el motivo de parada en stop_reason
    safety_info = {
        "stop_reason": response.stop_reason,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": response.model,
    }

    # Si el modelo se detuvo por end_turn es comportamiento normal;
    # si se detuvo por max_tokens, verificar si la respuesta está truncada
    if response.stop_reason == "max_tokens":
        safety_info["warning"] = "Respuesta truncada por límite de tokens"

    return {
        "text": response.content[0].text,
        "safety": safety_info
    }
