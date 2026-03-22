# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
OUTPUT_GUARDRAIL_PATTERNS = [
    # Detección de credenciales filtradas en la respuesta
    (r"(password|token|secret|api.?key)\s*[:=]\s*\S+", "SANITIZE",
     "credential_leak"),
    # Rutas internas del sistema operativo o del backend
    (r"(/app/|/backend/|/ai_service/|/var/lib/)", "SANITIZE",
     "internal_path"),
    # Exposición del system prompt del modelo
    (r"(system prompt|instrucciones del sistema|eres un asistente)",
     "SANITIZE", "prompt_exposure"),
    # Indicadores de alucinación — se registran pero no bloquean
    (r"(no tengo acceso|no puedo verificar|podría ser incorrecto)",
     "FLAG", "hallucination_indicator"),
]

def check_output_guardrails(response_text: str,
                             user_context: SecurityContext) -> GuardrailResult:
    """Filtra la respuesta del modelo antes de enviarla al usuario."""
    filtered = response_text
    for pattern, action, category in OUTPUT_GUARDRAIL_PATTERNS:
        if re.search(pattern, filtered, re.IGNORECASE):
            audit_log('GUARDRAIL_OUTPUT_TRIGGERED', severity='WARNING',
                     details=f"Category: {category}, action: {action}")
            if action == "SANITIZE":
                filtered = re.sub(pattern, "[REDACTADO]", filtered,
                                  flags=re.IGNORECASE)
            elif action == "BLOCK":
                return GuardrailResult(action="BLOCK", reason=category)
            elif action == "FLAG":
                # Registrar para análisis de calidad pero no modificar
                log_quality_event('hallucination_indicator', user_context)
    return GuardrailResult(action="ALLOW", filtered_text=filtered)
