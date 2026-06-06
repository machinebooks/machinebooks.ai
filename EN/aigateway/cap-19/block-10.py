# Extracted from: LibroAIGateway/cap-19-threat-jailbreak-dlp-pii.md
# SECRET: credentials and keys (dlp_service.py:65-85)
_SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "private_key_pem"),
    (r"AKIA[0-9A-Z]{16}", "aws_access_key"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "github_token"),
    (r"sk-[A-Za-z0-9]{20,}", "api_key_sk"),
    (r"sk-ant-[A-Za-z0-9\-_]{40,}", "anthropic_key"),
    (r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}", "jwt_token"),
    (r"(password|passwd|pwd|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "hardcoded_credential"),
]
