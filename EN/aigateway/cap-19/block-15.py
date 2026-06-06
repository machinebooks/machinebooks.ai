# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Cascading redaction (pii_redactor.py:58-69)
def redact_sensitive(text: str | None) -> str | None:
    if not text:
        return text
    result = text
    for pattern, replacement in _REDACT_PATTERNS:
        result = pattern.sub(replacement, result)
    return result
