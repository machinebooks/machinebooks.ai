# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/guardrails.py

import re
from dataclasses import dataclass
from typing import List

@dataclass
class GuardResult:
    """Resultado del pipeline de guardrails."""
    passed: bool
    violation_code: str | None = None
    violation_detail: str | None = None
    user_message: str | None = None
    pii_detected: List[str] | None = None

class InputGuardrails:
    """
    Pipeline de filtros de seguridad para entradas del copiloto.
    Se ejecuta ANTES de que el mensaje llegue al LLM.
    """

    MAX_MESSAGE_LENGTH = 4000  # Caracteres

    # Patrones conocidos de prompt injection
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"system\s*:\s*",
        r"<\|?(system|im_start|endoftext)\|?>",
        r"forget\s+(everything|all|your)\s+(you|instructions?|rules?)",
        r"nueva\s+instrucción\s+del\s+sistema",
        r"ignora\s+(las\s+)?(instrucciones|reglas)\s+(anteriores|previas)",
        r"actúa\s+como\s+(si\s+fueras|un)",
        r"eres\s+ahora\s+un",
        r"\[INST\]",
        r"<<SYS>>",
    ]

    # Patrones de PII (DNI, NIE, IBAN, tarjeta, email, teléfono)
    PII_PATTERNS = {
        "dni": r"\b\d{8}[A-Z]\b",
        "nie": r"\b[XYZ]\d{7}[A-Z]\b",
        "iban": r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b",
        "tarjeta": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "telefono": r"\b(\+34|0034)?\s?\d{3}\s?\d{3}\s?\d{3}\b",
    }

    async def scan(self, message: str) -> GuardResult:
        """Ejecuta todos los filtros en orden. El primero que falla bloquea."""

        # 1. Validar longitud
        if len(message) > self.MAX_MESSAGE_LENGTH:
            return GuardResult(
                passed=False,
                violation_code="MAX_LENGTH_EXCEEDED",
                violation_detail=f"Longitud: {len(message)}/{self.MAX_MESSAGE_LENGTH}",
                user_message=(
                    f"El mensaje excede el límite de {self.MAX_MESSAGE_LENGTH} "
                    f"caracteres. Por favor, reformula tu solicitud de forma más concisa."
                ),
            )

        # 2. Detectar prompt injection
        msg_lower = message.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, msg_lower, re.IGNORECASE):
                return GuardResult(
                    passed=False,
                    violation_code="PROMPT_INJECTION_DETECTED",
                    violation_detail=f"Patrón detectado: {pattern}",
                    user_message=(
                        "Se ha detectado un patrón no permitido en tu mensaje. "
                        "Si crees que es un error, reformula tu solicitud."
                    ),
                )

        # 3. Escanear PII
        pii_found = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, message):
                pii_found.append(pii_type)

        if pii_found:
            return GuardResult(
                passed=False,
                violation_code="PII_DETECTED",
                violation_detail=f"Tipos de PII detectados: {', '.join(pii_found)}",
                user_message=(
                    "Se han detectado posibles datos personales en tu mensaje "
                    f"({', '.join(pii_found)}). Por seguridad, el mensaje no se ha "
                    "enviado al modelo de IA. Reformula tu solicitud sin incluir "
                    "datos personales reales."
                ),
                pii_detected=pii_found,
            )

        return GuardResult(passed=True)
