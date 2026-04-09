# Extraido de: LibroAISafety/cap-22-arquitectura-segura.md
import re
from dataclasses import dataclass

@dataclass
class PIIDetection:
    type: str
    value: str
    position: tuple[int, int]
    confidence: float

# Patrones de PII para contexto español/europeo
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}",
    "nif": r"\b\d{8}[A-Z]\b",
    "iban": r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{2}\s?\d{10}\b",
    "phone_es": r"\b(?:\+34|0034)?\s?[6-9]\d{2}\s?\d{3}\s?\d{3}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

def filter_output(model_response: str) -> tuple[str, list[PIIDetection]]:
    """
    Escanea la respuesta del modelo buscando PII.
    Reemplaza detecciones por placeholders y retorna el listado.
    """
    detections = []
    filtered = model_response

    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, filtered):
            detections.append(PIIDetection(
                type=pii_type,
                value=match.group(),
                position=(match.start(), match.end()),
                confidence=0.9,  # ajustar con modelo ML para reducir falsos positivos
            ))
            filtered = filtered.replace(match.group(), f"[{pii_type.upper()}_REDACTED]")

    return filtered, detections
