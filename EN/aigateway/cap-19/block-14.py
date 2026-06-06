# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# Critical order: specific → general (pii_redactor.py:25-55)
_REDACT_PATTERNS: list[tuple[re.Pattern, str]] = [
    # First: technical keys and secrets (fixed format)
    (re.compile(r"-----BEGIN[^-]*PRIVATE KEY-----[\s\S]*?-----END[^-]*PRIVATE KEY-----"), "[REDACTED:private_key]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED:aws_key]"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{40,}"), "[REDACTED:anthropic_key]"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED:api_key]"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "[REDACTED:github_token]"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}"), "[REDACTED:jwt]"),

    # Then: generic credentials by field name
    (re.compile(r"(password|passwd|pwd|secret|api[_-]?token)\s*[:=]\s*['\"]?[^\s',;}]{8,}", re.I), "[REDACTED:credential]"),

    # Finally: personal PII (GDPR)
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED:email]"),
    (re.compile(r"\b\d{8}[A-Z]\b"), "[REDACTED:dni]"),
    (re.compile(r"\b[XYZ]\d{7}[A-Z]\b", re.I), "[REDACTED:nie]"),
    (re.compile(r"\b[A-Z]{2}\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}\b"), "[REDACTED:iban]"),
    (re.compile(r"\b(?:\+34[ -]?)?[6-9]\d{2}[ -]?\d{3}[ -]?\d{3}\b"), "[REDACTED:phone_es]"),
]
