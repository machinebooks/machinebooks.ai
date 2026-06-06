# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/moderation_service.py:98-154

@classmethod
async def evaluate_escalation(cls, db: AsyncSession, device_id: str, ...) -> str | None:
    """Evalúa si un dispositivo necesita escalación."""
    flags_warning = t.get("flags_for_warning", 5)
    flags_rate = t.get("flags_for_rate_reduction", 10)
    flags_suspend = t.get("flags_for_suspension", 20)

    # Contar flags en las últimas 24h y 7d
    count_24h = await db.execute(text("""
        SELECT COUNT(*) FROM moderation_actions
        WHERE device_id = :device_id
          AND action_taken IN ('block', 'flag', 'warn')
          AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """), {"device_id": device_id})
    flags_24h = count_24h.scalar() or 0

    # Determinar nivel de escalación
    if flags_7d >= flags_suspend:
        new_action = "suspension"
    elif flags_24h >= flags_rate:
        new_action = "rate_reduction"
    elif flags_24h >= flags_warning:
        new_action = "warning"
