# Extraído de: LibroDevSecOps/cap-13-prompt-injection.md
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class SecurityDecision:
    allowed: bool
    blocked_by: str | None
    details: dict
    timestamp: str

def process_secure_request(
    user_input: str,
    context: str = ""
) -> str | SecurityDecision:
    """Pipeline de 5 capas contra prompt injection."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Capa 1: Sanitización de input (< 1ms)
    sanitization = sanitize_input(user_input)
    if not sanitization.is_safe:
        return SecurityDecision(
            allowed=False,
            blocked_by="input_sanitization",
            details={"pattern": sanitization.matched_pattern},
            timestamp=timestamp
        )

    # Capa 5: Clasificador de inyección (200-500ms)
    # Se ejecuta antes del modelo principal para evitar coste innecesario
    classification = classify_injection(user_input)
    if classification.get("is_injection") and \
       classification.get("confidence", 0) > 0.7:
        return SecurityDecision(
            allowed=False,
            blocked_by="injection_classifier",
            details=classification,
            timestamp=timestamp
        )

    # Capa 2 + 3: System prompt hardened + Sandwich defense
    messages = build_sandwiched_messages(user_input, context)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=HARDENED_SYSTEM_PROMPT,
        messages=messages
    )
    response_text = response.content[0].text

    # Capa 4: Validación de output
    validation = validate_output(
        response_text,
        HARDENED_SYSTEM_PROMPT,
        user_input
    )
    if not validation.is_safe:
        # Registrar el incidente para análisis posterior
        log_security_event(
            event_type="output_violation",
            user_input=user_input,
            response=response_text,
            violations=validation.violations,
            timestamp=timestamp
        )
        return SecurityDecision(
            allowed=False,
            blocked_by="output_validation",
            details={"violations": validation.violations},
            timestamp=timestamp
        )

    return validation.sanitized_output


def log_security_event(**kwargs):
    """Registra eventos de seguridad para análisis y mejora continua."""
    # En producción: enviar a SIEM o a una tabla de auditoría
    event = {k: v for k, v in kwargs.items()}
    print(f"[SECURITY] {json.dumps(event, ensure_ascii=False)}")
