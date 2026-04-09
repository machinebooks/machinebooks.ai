# Extracted from: LibroAISafety/ch-06-guardrails.md
import re
from dataclasses import dataclass
from enum import Enum

class InputVerdict(Enum):
    ALLOW = "allow"       # Input passes to the model
    BLOCK = "block"       # Input is rejected
    FLAG = "flag"         # Input passes but is monitored

@dataclass
class GuardrailResult:
    verdict: InputVerdict
    reason: str
    rule_id: str          # Identifier of the rule that triggered

# Known prompt injection patterns
INJECTION_PATTERNS = [
    (r"ignore\s+(all\s+)?previous\s+instructions", "prompt_injection_ignore"),
    (r"you\s+are\s+now\s+(DAN|evil|unrestricted)", "prompt_injection_persona"),
    (r"system\s*prompt|system\s+instructions", "prompt_extraction_attempt"),
    (r"repeat\s+(everything|all|the\s+text)\s+(above|before)", "prompt_extraction_repeat"),
    (r"(?:act|behave|pretend)\s+as\s+(?:if\s+)?(?:you\s+)?(?:have\s+)?no\s+(?:restrictions|limits)",
     "prompt_injection_unrestrict"),
]

def check_input_guardrails(user_input: str) -> list[GuardrailResult]:
    """
    Evaluates user input against known patterns.
    Returns list of results — empty if no issues.
    """
    results = []
    normalized = user_input.lower().strip()

    # Prompt injection detection by patterns
    for pattern, rule_id in INJECTION_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            results.append(GuardrailResult(
                verdict=InputVerdict.BLOCK,
                reason=f"Injection pattern detected: {rule_id}",
                rule_id=rule_id
            ))

    # Anomalous length detection (many-shot, context stuffing)
    if len(user_input) > 50_000:
        results.append(GuardrailResult(
            verdict=InputVerdict.FLAG,
            reason=f"Abnormally long input: {len(user_input)} characters",
            rule_id="length_anomaly"
        ))

    # Suspicious encoding detection (base64, hex, unicode escaping)
    if re.search(r"(?:(?:[A-Za-z0-9+/]{4}){10,}={0,2})", user_input):
        results.append(GuardrailResult(
            verdict=InputVerdict.FLAG,
            reason="Possible base64 encoded content",
            rule_id="suspicious_encoding"
        ))

    return results
