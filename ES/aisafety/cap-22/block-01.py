# Extraido de: LibroAISafety/cap-22-arquitectura-segura.md
import re
from dataclasses import dataclass
from enum import Enum

class ThreatLevel(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"

@dataclass
class ValidationResult:
    level: ThreatLevel
    reason: str
    original_input: str
    sanitized_input: str | None

# Patrones de inyección conocidos — didáctico, no exhaustivo
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(?:a|an)\s+",
    r"system\s*:\s*",            # intento de inyectar rol system
    r"<\|im_start\|>",           # tokens de control ChatML
    r"\[INST\]",                 # tokens de control Llama
    r"Human:\s*\n\s*Assistant:",  # inyección de turno en Claude
]

def validate_input(user_input: str) -> ValidationResult:
    """
    Primera capa: detecta patrones de inyección conocidos.
    No intenta entender semántica — solo patrones sintácticos.
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return ValidationResult(
                level=ThreatLevel.BLOCKED,
                reason=f"Patrón de inyección detectado: {pattern}",
                original_input=user_input,
                sanitized_input=None,
            )

    # Heurísticas adicionales: longitud anómala, encoding sospechoso
    if len(user_input) > 50_000:  # many-shot suele requerir prompts largos
        return ValidationResult(
            level=ThreatLevel.SUSPICIOUS,
            reason="Input excede umbral de longitud (posible many-shot)",
            original_input=user_input,
            sanitized_input=user_input[:50_000],
        )

    return ValidationResult(
        level=ThreatLevel.SAFE,
        reason="",
        original_input=user_input,
        sanitized_input=user_input,
    )
