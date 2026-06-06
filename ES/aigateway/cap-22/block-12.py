# Extraído de: LibroAIGateway/cap-22-governance-engine.md
@classmethod
async def check(cls, db, organization_id, tool_name, role=None, user_id=None, device_id=None) -> str:
    rules = await cls.get_rules(db, organization_id)
    # get_rules() ordena por priority DESC

    for rule in rules:
        if not cls._matches_scope(rule, role, user_id, device_id):
            continue
        if not cls._matches_tool(rule, tool_name):
            continue
        return rule.behavior

    return "allow"  # Default: allow if no rule matches
