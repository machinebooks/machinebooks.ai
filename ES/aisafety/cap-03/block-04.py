# Extraido de: LibroAISafety/cap-03-dentro-del-modelo.md
# Verificación de integridad del contexto antes de envío
import hashlib

def verificar_integridad_contexto(
    system_prompt: str,
    mensajes: list[dict],
    max_tokens: int = 200_000
) -> dict:
    """Verifica que el system prompt está intacto y
    que el contexto total no desborda la ventana."""

    # Hash del system prompt para detectar modificaciones
    sp_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:16]

    # Estimación de tokens (aproximación: 4 chars ≈ 1 token)
    tokens_sp = len(system_prompt) // 4
    tokens_msgs = sum(len(m["content"]) // 4 for m in mensajes)
    tokens_total = tokens_sp + tokens_msgs

    alertas = []

    if tokens_total > max_tokens:
        alertas.append(
            f"CRITICO: contexto ({tokens_total}) supera ventana "
            f"({max_tokens}). Truncamiento probable."
        )

    ratio_sp = tokens_sp / max(tokens_total, 1)
    if ratio_sp < 0.03:
        alertas.append(
            f"AVISO: system prompt es {ratio_sp:.1%} del contexto. "
            f"Influencia reducida sobre generación."
        )

    return {
        "tokens_total": tokens_total,
        "tokens_system_prompt": tokens_sp,
        "ratio_sp": ratio_sp,
        "sp_hash": sp_hash,
        "alertas": alertas,
        "estado": "ok" if not alertas else "revisar"
    }
