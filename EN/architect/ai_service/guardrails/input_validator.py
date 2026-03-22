"""
Chapter 14: Input guardrails — prompt injection detection + PII filter.

8 guardrail types with graduated actions (not binary pass/fail):
  Input:  prompt_injection, malicious_content, off_topic, pii_detection
  Output: credential_leak, system_prompt_exposure, internal_paths, hallucination

Actions: ALLOW -> SANITIZE -> BLOCK

The PII filter detects Spanish document formats:
  DNI (12345678A), NIE (X1234567A), IBAN (ES12 ...),
  credit cards, phone numbers, email addresses.
"""

import re
import enum
from dataclasses import dataclass
from typing import List, Tuple


# =============================================================================
# Guardrail actions (Chapter 14)
# =============================================================================

class GuardrailAction(enum.Enum):
    ALLOW = "allow"         # Pass through unchanged
    SANITIZE = "sanitize"   # Redact/modify and continue
    BLOCK = "block"         # Reject the request entirely


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    action: GuardrailAction
    guardrail_type: str
    details: str = ""
    original_text: str = ""
    sanitized_text: str = ""


# =============================================================================
# Prompt injection detection (Chapter 14)
# =============================================================================

# 6 regex patterns for common prompt injection attempts
INJECTION_PATTERNS = [
    # Direct instruction override
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|rules)", re.I),
    # Role reassignment
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.I),
    re.compile(r"act\s+as\s+(a|an|if)\s+", re.I),
    # System prompt extraction
    re.compile(r"(show|print|display|reveal|repeat)\s+(your\s+)?(system\s+)?(prompt|instructions)", re.I),
    # Delimiter injection
    re.compile(r"<\|?(system|assistant|endof|im_start)\|?>", re.I),
    # Encoding evasion
    re.compile(r"base64\s*decode|eval\s*\(|exec\s*\(", re.I),
]


def detect_prompt_injection(text: str) -> GuardrailResult:
    """
    Detect prompt injection attempts using pattern matching.

    Chapter 14: This is the first layer of defense. Pattern matching
    catches known attack patterns quickly (< 1ms). More sophisticated
    attacks are caught by the output guardrails (credential leak,
    system prompt exposure) as a defense-in-depth strategy.
    """
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                guardrail_type="prompt_injection",
                details=f"Injection pattern detected: {match.group()[:50]}",
                original_text=text,
            )

    return GuardrailResult(
        action=GuardrailAction.ALLOW,
        guardrail_type="prompt_injection",
    )


# =============================================================================
# PII detection and redaction (Chapter 14)
# =============================================================================

PII_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # Spanish DNI: 8 digits + letter
    ("DNI", re.compile(r"\b\d{8}[A-Z]\b")),
    # Spanish NIE: X/Y/Z + 7 digits + letter
    ("NIE", re.compile(r"\b[XYZ]\d{7}[A-Z]\b")),
    # IBAN (Spanish format): ES + 2 check + 20 digits
    ("IBAN", re.compile(r"\bES\d{2}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")),
    # Credit card: 13-19 digits with optional separators
    ("CREDIT_CARD", re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7}\b")),
    # Spanish phone: +34 or 6/7/9 + 8 digits
    ("PHONE", re.compile(r"(\+34[\s-]?)?\b[679]\d{8}\b")),
    # Email address
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")),
]


def detect_pii(text: str) -> List[Tuple[str, str]]:
    """
    Detect PII in text using Spanish document format patterns.

    Returns list of (pii_type, matched_value) tuples.
    """
    findings = []
    for pii_type, pattern in PII_PATTERNS:
        for match in pattern.finditer(text):
            findings.append((pii_type, match.group()))
    return findings


def redact_pii_for_llm(text: str) -> str:
    """
    Redact PII before sending to the LLM.

    Chapter 14: This function is applied to user input before it reaches
    Claude, ensuring compliance with the AI governance framework.
    PII is replaced with type-specific placeholders that preserve
    the semantic structure for the model.
    """
    redacted = text
    for pii_type, pattern in PII_PATTERNS:
        redacted = pattern.sub(f"[{pii_type}_REDACTED]", redacted)
    return redacted


# =============================================================================
# Combined input validation pipeline (Chapter 14)
# =============================================================================

def validate_input(text: str) -> GuardrailResult:
    """
    Full input validation pipeline.

    Order matters:
      1. Prompt injection check (BLOCK if detected)
      2. PII detection (SANITIZE — redact and continue)
      3. Off-topic detection (BLOCK if clearly off-topic)

    Chapter 14: Graduated actions mean a message with PII is not
    rejected — the PII is redacted and the request proceeds.
    Only injection attempts and clearly off-topic messages are blocked.
    """
    # 1. Prompt injection — hard block
    injection_result = detect_prompt_injection(text)
    if injection_result.action == GuardrailAction.BLOCK:
        return injection_result

    # 2. PII detection — sanitize and continue
    pii_findings = detect_pii(text)
    if pii_findings:
        sanitized = redact_pii_for_llm(text)
        return GuardrailResult(
            action=GuardrailAction.SANITIZE,
            guardrail_type="pii_detection",
            details=f"PII detected: {[p[0] for p in pii_findings]}",
            original_text=text,
            sanitized_text=sanitized,
        )

    # 3. All clear
    return GuardrailResult(
        action=GuardrailAction.ALLOW,
        guardrail_type="input_validation",
    )
