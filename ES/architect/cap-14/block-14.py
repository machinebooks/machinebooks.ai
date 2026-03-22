# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class GuardrailAction(Enum):
    ALLOW = "allow"
    SANITIZE = "sanitize"
    BLOCK = "block"

@dataclass
class GuardrailResult:
    action: GuardrailAction
    reason: Optional[str] = None
    sanitized_text: Optional[str] = None

# Patrones de prompt injection (10 patrones: inglés y español)
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(?:a\s+)?(?:different|new|another)",
    r"reveal\s+(?:your\s+)?system\s+prompt",
    r"disregard\s+(?:your\s+)?(?:previous\s+)?instructions",
    r"act\s+as\s+(?:if\s+you\s+(?:are|were)\s+)?(?:a\s+different|an?\s+unrestricted)",
    r"jailbreak|dan\s+mode|developer\s+mode",
    # Patrones en español — cubren ataques formulados en el idioma del usuario
    r"ignora\s+(las\s+)?instrucciones\s+anteriores",
    r"ahora\s+eres\s+un",
    r"revela\s+tu\s+prompt\s+de\s+sistema",
    r"olvida\s+tus\s+restricciones",
]

# Expresiones para detección de PII
PII_PATTERNS = {
    "dni":     r"\b\d{8}[A-Z]\b",
    "nie":     r"\b[XYZ]\d{7}[A-Z]\b",
    "iban":    r"\bES\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "card":    r"\b(?:\d{4}[\s-]?){3}\d{4}\b",
    "phone":   r"\b(?:\+34\s?)?[6789]\d{8}\b",
    "email":   r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b",
}

def check_prompt_injection(text: str) -> GuardrailResult:
    """Detecta intentos de prompt injection con los 10 patrones registrados."""
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason=f"Posible prompt injection detectado"
            )
    return GuardrailResult(action=GuardrailAction.ALLOW)

def redact_pii_for_llm(text: str) -> tuple[str, bool]:
    """
    Sanitiza PII del texto antes de enviarlo a Claude.
    Retorna (texto_sanitizado, hubo_cambios).
    """
    modified = False
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        new_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", result)
        if new_text != result:
            modified = True
            result = new_text
    return result, modified

def run_input_guardrails(
    user_text: str,
    off_topic_patterns: list[str]
) -> GuardrailResult:
    """
    Ejecuta todos los guardrails de entrada en orden de severidad decreciente.
    La primera acción BLOCK o SANITIZE detiene la cadena.
    """
    # 1. Prompt injection (HIGH) — bloqueo inmediato
    result = check_prompt_injection(user_text)
    if result.action == GuardrailAction.BLOCK:
        return result

    # 2. Off-topic (MEDIUM) — bloqueo con mensaje
    for pattern in off_topic_patterns:
        if re.search(pattern, user_text, re.IGNORECASE):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Consulta fuera del ámbito de la Plataforma"
            )

    # 3. PII (MEDIUM) — sanitización antes de enviar a Claude
    sanitized, had_pii = redact_pii_for_llm(user_text)
    if had_pii:
        return GuardrailResult(
            action=GuardrailAction.SANITIZE,
            reason="PII detectado y eliminado para protección de datos",
            sanitized_text=sanitized
        )

    return GuardrailResult(action=GuardrailAction.ALLOW)
