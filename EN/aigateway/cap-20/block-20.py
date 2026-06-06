# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/moderation_service.py:25-60

@classmethod
async def log_moderation(cls, db: AsyncSession, request_id: str, device_id: str,
                         employee_id, organization_id, direction,
                         category_slug, classifier, violation_type,
                         action_taken, severity="medium", details=None) -> int:
    """Records a moderation action."""
    action = ModerationAction(
        organization_id=organization_id,
        request_id=request_id,
        device_id=device_id,
        employee_id=employee_id,
        direction=direction,
        category_slug=category_slug,
        classifier=classifier,       # msj_defense, output_filter, content_classifier, pii, dlp
        violation_type=violation_type,
        action_taken=action_taken,   # block, redact, flag, warn, allow
        severity=severity,
        details=details,
        created_at=datetime.utcnow(),
    )
    db.add(action)
    await db.flush()
    return action.id
