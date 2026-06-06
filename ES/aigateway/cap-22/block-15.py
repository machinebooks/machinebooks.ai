# Extraído de: LibroAIGateway/cap-22-governance-engine.md
@classmethod
async def delete_rule(cls, db, rule_id) -> bool:
    rule = await cls._get_rule(db, rule_id)
    if not rule:
        return False
    rule.is_active = False  # Soft delete — audit trail preservado
    await db.commit()
    return True
