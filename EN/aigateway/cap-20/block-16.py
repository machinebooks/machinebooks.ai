# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/output_filter_service.py:42-55

_CODE_VULNERABILITY_PATTERNS = [
    (re.compile(r"""(password|passwd|pwd|secret|api_key|apikey|token|auth)\s*=\s*['"]\S{8,}['"]""", re.IGNORECASE), "hardcoded_credential"),
    (re.compile(r"\b(eval|exec)\s*\(\s*(request|input|user|data|params)", re.IGNORECASE), "eval_injection"),
    (re.compile(r"""(execute|query|cursor)\s*\(\s*f?['"]SELECT|INSERT|UPDATE|DELETE\s.*{"""", re.IGNORECASE), "sql_injection_vuln"),
    (re.compile(r"\b(pickle\.loads?|yaml\.load\s*\(?(?!.*Loader))", re.IGNORECASE), "insecure_deserialization"),
    (re.compile(r"(subprocess|os\.system|os\.popen|exec\s*\()\\s*\(\\s*.*\\b(curl|wget|nc|netcat|bash|sh)\\b", re.IGNORECASE), "backdoor_pattern"),
]
