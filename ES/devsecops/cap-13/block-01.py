# Extraído de: LibroDevSecOps/cap-13-prompt-injection.md
import re
from dataclasses import dataclass

@dataclass
class SanitizationResult:
    is_safe: bool
    matched_pattern: str | None
    original_input: str

# Patrones conocidos de prompt injection (no exhaustivos)
INJECTION_PATTERNS = [
    r"(?i)ignor(a|e)\s+(todas?\s+)?(las?\s+)?instrucciones?\s+(previas?|anteriores?)",
    r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"(?i)system\s*prompt",
    r"(?i)eres\s+ahora\s+(un|una)\s+",
    r"(?i)you\s+are\s+now\s+",
    r"(?i)do\s+anything\s+now",
    r"(?i)modo\s+(desarrollador|dios|admin)",
    r"(?i)developer\s+mode",
    r"(?i)jailbreak",
    r"(?i)repite\s+(textualmente|exactamente)\s+(las?\s+)?instrucciones",
    r"(?i)repeat\s+(your|the)\s+(system\s+)?instructions?",
    r"(?i)\[INST\]",           # Tokens de control de LLMs
    r"(?i)<\|im_start\|>",    # Tokens de chat de formato OpenAI
    r"(?i)<<SYS>>",           # Tokens de sistema Llama
]

def sanitize_input(user_input: str) -> SanitizationResult:
    """Filtra patrones conocidos de prompt injection."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input):
            return SanitizationResult(
                is_safe=False,
                matched_pattern=pattern,
                original_input=user_input
            )
    return SanitizationResult(
        is_safe=True,
        matched_pattern=None,
        original_input=user_input
    )
