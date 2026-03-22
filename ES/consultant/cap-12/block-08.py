# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
class ConfidentialityGuard:
    """Protección de datos confidenciales en el flujo de auditoría."""

    def __init__(self, sensitivity_config: dict):
        self.patterns_to_redact = sensitivity_config.get("redact_patterns", [])
        self.allowed_domains = sensitivity_config.get("allowed_domains", [])

    def sanitize_before_api(self, text: str) -> str:
        """Elimina datos sensibles antes de enviar a la API."""
        import re
        sanitized = text
        for pattern_config in self.patterns_to_redact:
            pattern = pattern_config["regex"]
            replacement = pattern_config["replacement"]
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def verify_data_residency(self, api_endpoint: str) -> bool:
        """Verifica que el endpoint cumple requisitos de residencia."""
        return any(
            domain in api_endpoint
            for domain in self.allowed_domains
        )

# Configuración típica para sector público español
SECTOR_PUBLICO_CONFIG = {
    "redact_patterns": [
        {"regex": r"\b\d{8}[A-Z]\b", "replacement": "[DNI_REDACTED]"},
        {"regex": r"\b[A-Z]\d{8}\b", "replacement": "[NIE_REDACTED]"},
        {"regex": r"[\w.]+@[\w.]+\.\w+", "replacement": "[EMAIL_REDACTED]"},
        {"regex": r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "replacement": "[IP_REDACTED]"},
    ],
    "allowed_domains": ["api.anthropic.com"]
}
