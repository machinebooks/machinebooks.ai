# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
# Defensive whitelist — only explicit tables and columns
_PSEUDONYMIZE_FIELDS = {
    "audit_logs": ["employee_id"],
}

# Sanitized identifiers: only letters, numbers, underscore
def _safe_identifier(name: str) -> bool:
    return bool(name) and all(c.isalnum() or c == "_" for c in name)
