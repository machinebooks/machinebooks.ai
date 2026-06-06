# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
# Whitelist defensiva — solo tablas y columnas explícitas
_PSEUDONYMIZE_FIELDS = {
    "audit_logs": ["employee_id"],
}

# Identifiers sanitizados: solo letras, números, underscore
def _safe_identifier(name: str) -> bool:
    return bool(name) and all(c.isalnum() or c == "_" for c in name)
