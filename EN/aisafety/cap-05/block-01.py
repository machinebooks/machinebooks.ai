# Extracted from: LibroAISafety/ch-05-system-prompt.md
# Basic system prompt isolation
def build_messages(system_instructions: str, user_input: str) -> list:
    """
    Builds messages with isolation between system prompt and user input.
    The delimiter reduces (does not eliminate) the injection risk.
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
