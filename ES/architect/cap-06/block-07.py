# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions?|prompts?)",
    r"you\s+are\s+now\s+",
    r"system\s*:\s*",
    r"<\|?(system|im_start|endoftext)\|?>",
    r"IMPORTANT:\s*ignore",
    r"forget\s+(everything|all|your)\s+(you|instructions?)",
]

def check_prompt_injection(text: str) -> GuardrailResult:
    """Verifica patrones de prompt injection en input de usuario."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(
                action="BLOCK",
                reason=f"Prompt injection detectado: {pattern}",
                severity="CRITICAL"
            )
    return GuardrailResult(action="ALLOW")
