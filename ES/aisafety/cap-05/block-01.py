# Extraido de: LibroAISafety/cap-05-system-prompt.md
# Aislamiento básico de system prompt
def build_messages(system_instructions: str, user_input: str) -> list:
    """
    Construye mensajes con aislamiento entre system prompt y entrada del usuario.
    El delimitador reduce (no elimina) el riesgo de inyección.
    """
    return [
        {
            "role": "system",
            "content": system_instructions
        },
        {
            "role": "user",
            "content": f"<user_message>\n{user_input}\n</user_message>"
        }
    ]
