# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
# Redact PII before encrypting — defense in depth
payload = {
    "system_prompt": redact_sensitive(system_prompt_text),
    "user_message": redact_sensitive(user_message_text),
    "response": redact_sensitive(response_text),
}
