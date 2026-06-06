# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/firewall_service.py:229-259

async def record(*, category: str, action_taken: str, ...) -> None:
    """Registra en firewall_events con sesión aislada."""
    severity = severity_for(category)
    allowed = action_taken != ACTION_BLOCK
    try:
        async with AsyncSessionLocal() as fdb:
            await fdb.execute(text(
                "INSERT INTO firewall_events ("
                "  request_id, category, severity, action_taken, allowed, direction, "
                "  reason, match_excerpt, user_id, organization_id, team_id, device_id, "
                "  surface, surface_detail, conversation_id"
                ") VALUES ("
                "  :rid, :cat, :sev, :act, :allowed, :dir, :reason, :excerpt, "
                "  :uid, :oid, :tid, :did, :surf, :sdetail, :cid"
                ")"
            ), {
                "rid": (request_id or "")[:64] or None,
                "cat": category[:32],
                "sev": severity[:16],
                "act": action_taken[:16],
                # ... resto de campos truncados por seguridad
            })
            await fdb.commit()
    except Exception:
        logger.exception("firewall:event_record_failed category=%s", category)
