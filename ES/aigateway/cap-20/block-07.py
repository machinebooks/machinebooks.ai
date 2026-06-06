# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/guardrail_service.py:129-148

async def _persist_events(events: list[GuardrailEvent], hit_ids: list[int]) -> None:
    """Persiste eventos en una sesión nueva para no contaminar el request."""
    if not events:
        return
    try:
        async with AsyncSessionLocal() as persist_db:
            persist_db.add_all(events)
            await persist_db.execute(
                update(Guardrail)
                .where(Guardrail.id.in_(hit_ids))
                .values(hit_count=Guardrail.hit_count + 1, last_hit_at=datetime.utcnow())
            )
            await persist_db.commit()
    except Exception:
        logger.exception("guardrail:event_persist_failed")
