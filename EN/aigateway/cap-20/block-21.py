# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/moderation_service.py:98-154

@classmethod
async def evaluate_escalation(cls, db: AsyncSession, device_id: str, ...) -> str | None:
    """Evaluates whether a device needs escalation."""
    flags_warning = t.get("flags_for_warning", 5)
    flags_rate = t.get("flags_for_rate_reduction", 10)
    flags_suspend = t.get("flags_for_suspension", 20)

    # Count flags in the last 24h and 7d
    count_24h = await db.execute(text("""
        SELECT COUNT(*) FROM moderation_actions
        WHERE device_id = :device_id
          AND action_taken IN ('block', 'flag', 'warn')
          AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """), {"device_id": device_id})
    flags_24h = count_24h.scalar() or 0

    # Determine escalation level
    if flags_7d >= flags_suspend:
        new_action = "suspension"
    elif flags_24h >= flags_rate:
        new_action = "rate_reduction"
    elif flags_24h >= flags_warning:
        new_action = "warning"
