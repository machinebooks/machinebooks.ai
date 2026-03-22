# Extraído de: LibroConsultor/cap-23-confidencialidad.md
import anthropic
import re
from dataclasses import dataclass
from enum import Enum

class SensitivityLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class ClassificationResult:
    level: SensitivityLevel
    reasons: list[str]
    entities_found: list[str]
    recommendation: str  # "api_direct", "api_sanitized", "local_only"

# Patrones deterministas para detección rápida
RESTRICTED_PATTERNS = {
    "dni_nie": r"\b\d{8}[A-Z]\b|\b[XYZ]\d{7}[A-Z]\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "iban": r"\b[A-Z]{2}\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}\b",
    "phone_spain": r"\b(?:\+34|0034)?\s?[6-9]\d{8}\b",
}

CONFIDENTIAL_KEYWORDS = [
    "vulnerabilidad", "hallazgo", "brecha", "incidente",
    "contraseña", "credencial", "organigrama", "nómina",
    "expediente", "sanción", "despido", "reclamación",
]

def classify_deterministic(text: str) -> tuple[SensitivityLevel, list[str]]:
    """Clasificación rápida basada en patrones regex."""
    entities = []
    for name, pattern in RESTRICTED_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            entities.extend([f"{name}: {m[:4]}***" for m in matches])

    if entities:
        return SensitivityLevel.RESTRICTED, entities

    for keyword in CONFIDENTIAL_KEYWORDS:
        if keyword.lower() in text.lower():
            return SensitivityLevel.CONFIDENTIAL, [keyword]

    return SensitivityLevel.PUBLIC, []
