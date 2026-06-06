# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/output_filter_service.py:58-70

_OUTPUT_PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "email"),
    (re.compile(r"\b\d{8,9}[A-Z]\b"), "dni_nie"),
    (re.compile(r"\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,4}\b"), "iban"),
    (re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"), "credit_card"),
    (re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "aws_access_key"),
    (re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"), "private_key"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "jwt_token"),
]
