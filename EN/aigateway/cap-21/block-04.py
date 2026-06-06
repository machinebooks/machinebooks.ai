# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
async def _get_prev_hash(db: AsyncSession, before_id: int) -> str:
    stmt = (
        select(AuditLog.id, AuditLog.chain_hash)
        .where(AuditLog.id < before_id, AuditLog.chain_hash.isnot(None))
        .order_by(AuditLog.id.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.first()
    if row is None:
        return GENESIS_HASH if before_id <= 1 else f"chain_gap_{before_id}"
    prev_id, prev_hash = row
    if prev_id != before_id - 1:
        return f"chain_gap_{before_id}"
    return prev_hash or GENESIS_HASH
