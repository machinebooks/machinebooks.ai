# Extracted from: LibroAISafety/ch-03-inside-the-model.md
# Context integrity verification before sending
import hashlib

def verify_context_integrity(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 200_000
) -> dict:
    """Verifies that the system prompt is intact and
    that the total context does not overflow the window."""

    # Hash of the system prompt to detect modifications
    sp_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:16]

    # Token estimation (approximation: 4 chars ≈ 1 token)
    tokens_sp = len(system_prompt) // 4
    tokens_msgs = sum(len(m["content"]) // 4 for m in messages)
    tokens_total = tokens_sp + tokens_msgs

    alerts = []

    if tokens_total > max_tokens:
        alerts.append(
            f"CRITICAL: context ({tokens_total}) exceeds window "
            f"({max_tokens}). Truncation likely."
        )

    ratio_sp = tokens_sp / max(tokens_total, 1)
    if ratio_sp < 0.03:
        alerts.append(
            f"WARNING: system prompt is {ratio_sp:.1%} of context. "
            f"Reduced influence on generation."
        )

    return {
        "tokens_total": tokens_total,
        "tokens_system_prompt": tokens_sp,
        "ratio_sp": ratio_sp,
        "sp_hash": sp_hash,
        "alerts": alerts,
        "status": "ok" if not alerts else "review"
    }
