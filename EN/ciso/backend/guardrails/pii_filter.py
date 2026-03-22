# Chapter 13 — PII filter for LLM input/output
#
# Scans messages before they reach the LLM (input guardrail) and
# responses before they reach the user (output guardrail).
# In a GRC, users may accidentally paste real personal data from
# a data subject into a chat — those data must not travel to a
# cloud LLM provider without consent.
#
# Uses the same PII patterns from Chapter 6 (pii_detector.py),
# integrated into the guardrails pipeline from Chapter 13.

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GuardResult:
    """Result of the guardrails pipeline."""
    passed: bool
    violation_code: Optional[str] = None
    violation_detail: Optional[str] = None
    user_message: Optional[str] = None
    pii_detected: Optional[list[str]] = None


class InputGuardrails:
    """Pipeline of security filters for copilot inputs.

    Executes BEFORE the message reaches the LLM.
    Order matters: length (trivial) -> injection (patterns) -> PII (regex).

    Usage:
        guardrails = InputGuardrails()
        result = await guardrails.scan("My DNI is 12345678Z and my IBAN is ES1234...")
        if not result.passed:
            return error_response(result.user_message)
    """

    MAX_MESSAGE_LENGTH = 4000  # Characters

    # Prompt injection patterns (from Chapter 13)
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"system\s*:\s*",
        r"<\|?(system|im_start|endoftext)\|?>",
        r"forget\s+(everything|all|your)\s+(you|instructions?|rules?)",
        r"nueva\s+instrucci[oó]n\s+del\s+sistema",
        r"ignora\s+(las\s+)?(instrucciones|reglas)\s+(anteriores|previas)",
        r"act[uú]a\s+como\s+(si\s+fueras|un)",
        r"eres\s+ahora\s+un",
        r"\[INST\]",
        r"<<SYS>>",
    ]

    # PII patterns (DNI, NIE, IBAN, credit card, email, phone)
    PII_PATTERNS = {
        "dni": r"\b\d{8}[A-Z]\b",
        "nie": r"\b[XYZ]\d{7}[A-Z]\b",
        "iban": r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b",
        "credit_card": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        "email": r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b",
        "phone_es": r"\b(?:\+34|0034)?\s?\d{3}\s?\d{3}\s?\d{3}\b",
    }

    async def scan(self, message: str) -> GuardResult:
        """Execute all filters in order. The first failure blocks."""

        # 1. Validate length
        if len(message) > self.MAX_MESSAGE_LENGTH:
            return GuardResult(
                passed=False,
                violation_code="MAX_LENGTH_EXCEEDED",
                violation_detail=f"Length: {len(message)}/{self.MAX_MESSAGE_LENGTH}",
                user_message=(
                    f"Message exceeds the {self.MAX_MESSAGE_LENGTH} character limit. "
                    f"Please rephrase your request more concisely."
                ),
            )

        # 2. Detect prompt injection
        msg_lower = message.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, msg_lower, re.IGNORECASE):
                return GuardResult(
                    passed=False,
                    violation_code="PROMPT_INJECTION_DETECTED",
                    violation_detail=f"Pattern matched: {pattern}",
                    user_message=(
                        "A disallowed pattern was detected in your message. "
                        "If you believe this is an error, please rephrase your request."
                    ),
                )

        # 3. Scan for PII
        pii_found = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, message):
                pii_found.append(pii_type)

        if pii_found:
            return GuardResult(
                passed=False,
                violation_code="PII_DETECTED",
                violation_detail=f"PII types detected: {', '.join(pii_found)}",
                user_message=(
                    f"Possible personal data detected in your message "
                    f"({', '.join(pii_found)}). For security, the message was not "
                    f"sent to the AI model. Please rephrase without including "
                    f"real personal data."
                ),
                pii_detected=pii_found,
            )

        return GuardResult(passed=True)
