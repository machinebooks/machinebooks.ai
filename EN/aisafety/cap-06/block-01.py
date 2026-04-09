# Extracted from: LibroAISafety/ch-06-guardrails.md
import re
from typing import Optional

# Common PII patterns (international)
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_us": r"(?:\+1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",
    "credit_card": r"\b(?:\d{4}[\s.-]?){3}\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "iban": r"\b[A-Z]{2}\d{2}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{2}[\s.-]?\d{10}\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "aws_key": r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}",
}

def scan_output_for_pii(
    response_text: str,
    patterns: dict = PII_PATTERNS
) -> dict:
    """
    Scans the model response looking for PII.
    Returns a dictionary with the types of PII found.
    """
    findings = {}
    for pii_type, pattern in patterns.items():
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        if matches:
            findings[pii_type] = {
                "count": len(matches),
                "action": "redact"  # Replace with placeholder
            }
    return findings


def redact_pii(
    response_text: str,
    patterns: dict = PII_PATTERNS
) -> str:
    """
    Replaces detected PII with placeholders.
    Preserves the response context.
    """
    redacted = response_text
    for pii_type, pattern in patterns.items():
        placeholder = f"[{pii_type.upper()}_REDACTED]"
        redacted = re.sub(pattern, placeholder, redacted, flags=re.IGNORECASE)
    return redacted
