# Extracted from: LibroAISafety/ch-22-secure-architecture.md
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

# Known injection patterns -- didactic, not exhaustive
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(?:a|an)\s+",
    r"system\s*:\s*",            # attempt to inject system role
    r"<\|im_start\|>",           # ChatML control tokens
    r"\[INST\]",                 # Llama control tokens
    r"Human:\s*\n\s*Assistant:",  # turn injection in Claude
]

def validate_input(user_input: str) -> ValidationResult:
    """
    First layer: detects known injection patterns.
    Does not attempt to understand semantics -- only syntactic patterns.
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return ValidationResult(
                level=ThreatLevel.BLOCKED,
                reason=f"Injection pattern detected: {pattern}",
                original_input=user_input,
                sanitized_input=None,
            )

    # Additional heuristics: anomalous length, suspicious encoding
    if len(user_input) > 50_000:  # many-shot typically requires long prompts
        return ValidationResult(
            level=ThreatLevel.SUSPICIOUS,
            reason="Input exceeds length threshold (possible many-shot)",
            original_input=user_input,
            sanitized_input=user_input[:50_000],
        )

    return ValidationResult(
        level=ThreatLevel.SAFE,
        reason="",
        original_input=user_input,
        sanitized_input=user_input,
    )
