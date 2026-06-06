# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
batcher = get_audit_batcher()
if getattr(batcher, "_task", None) is None:
    # Direct INSERT for Celery workers without a drainer
    row = AuditLog(**payload)
    db.add(row)
    await db.commit()
