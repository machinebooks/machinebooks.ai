# Extraído de: LibroCISO/cap-06-brechas-encargados-transferencias.md
# Detector de PII — patrones regex para datos personales españoles
# Modo warn-only: registra alertas sin bloquear la operación

import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PIIType(str, Enum):
    """Tipos de datos personales detectables."""
    DNI = "dni"               # Documento Nacional de Identidad
    NIE = "nie"               # Número de Identidad de Extranjero
    PASSPORT = "passport"     # Pasaporte español
    IBAN = "iban"             # Cuenta bancaria internacional
    CREDIT_CARD = "credit_card"
    PHONE = "phone"           # Teléfono español
    EMAIL = "email"
    IP_ADDRESS = "ip_address"
    NASS = "nass"             # Número Afiliación Seguridad Social
    HEALTH_CARD = "health_card"  # Tarjeta sanitaria (CIP)


@dataclass
class PIIMatch:
    """Un dato personal detectado en el texto."""
    pii_type: PIIType
    value_masked: str       # Valor enmascarado: "12***678A"
    position: int           # Posición en el texto original
    confidence: float       # 0.0 a 1.0
    context: str            # Texto circundante (para revisión)


@dataclass
class PIIScanResult:
    """Resultado del escaneo de un texto."""
    text_length: int
    matches: list[PIIMatch] = field(default_factory=list)
    scan_time_ms: float = 0.0

    @property
    def has_pii(self) -> bool:
        return len(self.matches) > 0

    @property
    def high_confidence_matches(self) -> list[PIIMatch]:
        return [m for m in self.matches if m.confidence >= 0.8]


# --- Patrones regex para PII españoles ---

# DNI: 8 dígitos + letra de control
# La letra se valida contra la tabla oficial del Ministerio del Interior
DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
DNI_PATTERN = re.compile(
    r'\b(\d{8})\s*[-]?\s*([A-HJ-NP-TV-Z])\b',
    re.IGNORECASE
)

# NIE: X/Y/Z + 7 dígitos + letra de control
NIE_PATTERN = re.compile(
    r'\b([XYZ])\s*[-]?\s*(\d{7})\s*[-]?\s*([A-Z])\b',
    re.IGNORECASE
)

# IBAN español: ES + 2 dígitos control + 20 dígitos
IBAN_ES_PATTERN = re.compile(
    r'\b(ES)\s*(\d{2})\s*(\d{4})\s*(\d{4})\s*(\d{2})\s*(\d{10})\b'
)

# Número de la Seguridad Social: 12 dígitos
NASS_PATTERN = re.compile(
    r'\b(\d{2})\s*[-/]?\s*(\d{8})\s*[-/]?\s*(\d{2})\b'
)

# Teléfono español: 9 dígitos empezando por 6, 7 o 9
PHONE_PATTERN = re.compile(
    r'\b(\+34\s*)?([679]\d{8})\b'
)

# Tarjeta de crédito: 13-19 dígitos (validación Luhn posterior)
CREDIT_CARD_PATTERN = re.compile(
    r'\b(\d{4})\s*[-]?\s*(\d{4})\s*[-]?\s*(\d{4})\s*[-]?\s*(\d{1,7})\b'
)

# Email
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)

# Dirección IP v4
IP_PATTERN = re.compile(
    r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b'
)


def _validate_dni_letter(digits: str, letter: str) -> bool:
    """Valida la letra de control del DNI español."""
    try:
        idx = int(digits) % 23
        return DNI_LETTERS[idx].upper() == letter.upper()
    except (ValueError, IndexError):
        return False


def _validate_nie_letter(prefix: str, digits: str, letter: str) -> bool:
    """Valida la letra de control del NIE español."""
    nie_prefix_map = {"X": "0", "Y": "1", "Z": "2"}
    full_number = nie_prefix_map.get(prefix.upper(), "0") + digits
    return _validate_dni_letter(full_number, letter)


def _mask_value(value: str) -> str:
    """Enmascara un valor dejando visible inicio y final."""
    if len(value) <= 4:
        return "***"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def _luhn_check(number: str) -> bool:
    """Algoritmo de Luhn para validar tarjetas de crédito."""
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def scan_text_for_pii(
    text: str,
    context_chars: int = 30
) -> PIIScanResult:
    """Escanea un texto buscando datos personales.

    Aplica patrones regex con validación de control
    para reducir falsos positivos. Devuelve matches
    con confianza calculada y contexto para revisión.
    """
    import time
    start = time.monotonic()
    matches = []

    # --- DNI ---
    for m in DNI_PATTERN.finditer(text):
        digits, letter = m.group(1), m.group(2)
        valid = _validate_dni_letter(digits, letter)
        confidence = 0.95 if valid else 0.4
        ctx_start = max(0, m.start() - context_chars)
        ctx_end = min(len(text), m.end() + context_chars)
        matches.append(PIIMatch(
            pii_type=PIIType.DNI,
            value_masked=_mask_value(digits + letter),
            position=m.start(),
            confidence=confidence,
            context=text[ctx_start:ctx_end]
        ))

    # --- NIE ---
    for m in NIE_PATTERN.finditer(text):
        prefix, digits, letter = m.group(1), m.group(2), m.group(3)
        valid = _validate_nie_letter(prefix, digits, letter)
        confidence = 0.95 if valid else 0.4
        ctx_start = max(0, m.start() - context_chars)
        ctx_end = min(len(text), m.end() + context_chars)
        matches.append(PIIMatch(
            pii_type=PIIType.NIE,
            value_masked=_mask_value(prefix + digits + letter),
            position=m.start(),
            confidence=confidence,
            context=text[ctx_start:ctx_end]
        ))

    # --- IBAN español ---
    for m in IBAN_ES_PATTERN.finditer(text):
        full_iban = "".join(m.groups())
        confidence = 0.90  # IBAN con prefijo ES tiene alta confianza
        ctx_start = max(0, m.start() - context_chars)
        ctx_end = min(len(text), m.end() + context_chars)
        matches.append(PIIMatch(
            pii_type=PIIType.IBAN,
            value_masked=_mask_value(full_iban),
            position=m.start(),
            confidence=confidence,
            context=text[ctx_start:ctx_end]
        ))

    # --- Tarjeta de crédito (con validación Luhn) ---
    for m in CREDIT_CARD_PATTERN.finditer(text):
        card_number = "".join(m.groups())
        if _luhn_check(card_number):
            ctx_start = max(0, m.start() - context_chars)
            ctx_end = min(len(text), m.end() + context_chars)
            matches.append(PIIMatch(
                pii_type=PIIType.CREDIT_CARD,
                value_masked=_mask_value(card_number),
                position=m.start(),
                confidence=0.92,
                context=text[ctx_start:ctx_end]
            ))

    # --- NASS ---
    for m in NASS_PATTERN.finditer(text):
        nass_number = "".join(m.groups())
        if len(nass_number) == 12:
            ctx_start = max(0, m.start() - context_chars)
            ctx_end = min(len(text), m.end() + context_chars)
            matches.append(PIIMatch(
                pii_type=PIIType.NASS,
                value_masked=_mask_value(nass_number),
                position=m.start(),
                confidence=0.6,  # Alta tasa de falsos positivos
                context=text[ctx_start:ctx_end]
            ))

    elapsed_ms = (time.monotonic() - start) * 1000
    return PIIScanResult(
        text_length=len(text),
        matches=matches,
        scan_time_ms=round(elapsed_ms, 2)
    )
