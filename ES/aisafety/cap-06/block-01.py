# Extraido de: LibroAISafety/cap-06-guardrails.md
import re
from typing import Optional

# Patrones de PII comunes (España + internacional)
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_es": r"(?:\+34[\s.-]?)?(?:6|7|9)\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}",
    "credit_card": r"\b(?:\d{4}[\s.-]?){3}\d{4}\b",
    "dni_nie": r"\b[0-9XYZ]\d{7}[A-Z]\b",
    "iban_es": r"\bES\d{2}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{2}[\s.-]?\d{10}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "aws_key": r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}",
}

def scan_output_for_pii(
    response_text: str,
    patterns: dict = PII_PATTERNS
) -> dict:
    """
    Escanea la respuesta del modelo buscando PII.
    Retorna un diccionario con los tipos de PII encontrados.
    """
    findings = {}
    for pii_type, pattern in patterns.items():
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        if matches:
            findings[pii_type] = {
                "count": len(matches),
                "action": "redact"  # Sustituir por placeholder
            }
    return findings


def redact_pii(
    response_text: str,
    patterns: dict = PII_PATTERNS
) -> str:
    """
    Sustituye PII detectada por placeholders.
    Preserva el contexto de la respuesta.
    """
    redacted = response_text
    for pii_type, pattern in patterns.items():
        placeholder = f"[{pii_type.upper()}_REDACTED]"
        redacted = re.sub(pattern, placeholder, redacted, flags=re.IGNORECASE)
    return redacted
