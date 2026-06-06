# Extraído de: LibroAIGateway/cap-21-audit-append-only.md
# Redactar PII antes de cifrar — defensa en profundidad
payload = {
    "system_prompt": redact_sensitive(system_prompt_text),
    "user_message": redact_sensitive(user_message_text),
    "response": redact_sensitive(response_text),
}
