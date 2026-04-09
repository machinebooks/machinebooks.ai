# Extraido de: LibroAISafety/cap-06-guardrails.md
import re
from dataclasses import dataclass
from enum import Enum

class InputVerdict(Enum):
    ALLOW = "allow"       # La entrada pasa al modelo
    BLOCK = "block"       # La entrada se rechaza
    FLAG = "flag"         # La entrada pasa pero se monitoriza

@dataclass
class GuardrailResult:
    verdict: InputVerdict
    reason: str
    rule_id: str          # Identificador de la regla que disparó

# Patrones conocidos de inyección de prompt
INJECTION_PATTERNS = [
    (r"ignore\s+(all\s+)?previous\s+instructions", "prompt_injection_ignore"),
    (r"you\s+are\s+now\s+(DAN|evil|unrestricted)", "prompt_injection_persona"),
    (r"system\s*prompt|instrucciones?\s+del?\s+sistema", "prompt_extraction_attempt"),
    (r"repeat\s+(everything|all|the\s+text)\s+(above|before)", "prompt_extraction_repeat"),
    (r"(?:act|behave|pretend)\s+as\s+(?:if\s+)?(?:you\s+)?(?:have\s+)?no\s+(?:restrictions|limits)",
     "prompt_injection_unrestrict"),
]

def check_input_guardrails(user_input: str) -> list[GuardrailResult]:
    """
    Evalúa la entrada del usuario contra patrones conocidos.
    Retorna lista de resultados — vacía si no hay problemas.
    """
    results = []
    normalized = user_input.lower().strip()

    # Detección de inyección de prompt por patrones
    for pattern, rule_id in INJECTION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            results.append(GuardrailResult(
                verdict=InputVerdict.BLOCK,
                reason=f"Patrón de inyección detectado: {rule_id}",
                rule_id=rule_id
            ))

    # Detección de longitud anómala (many-shot, context stuffing)
    if len(user_input) > 50_000:
        results.append(GuardrailResult(
            verdict=InputVerdict.FLAG,
            reason=f"Entrada anormalmente larga: {len(user_input)} caracteres",
            rule_id="length_anomaly"
        ))

    # Detección de encoding sospechoso (base64, hex, unicode escaping)
    if re.search(r"(?:(?:[A-Za-z0-9+/]{4}){10,}={0,2})", user_input):
        results.append(GuardrailResult(
            verdict=InputVerdict.FLAG,
            reason="Posible contenido codificado en base64",
            rule_id="suspicious_encoding"
        ))

    return results
