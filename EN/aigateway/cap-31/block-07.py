# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Parameterized multi-tenant filter — gateway/app/api/v1/compliance_portal.py:121-140
def _org_clause(current: dict, column: str, param_suffix: str = "") -> tuple[str, dict]:
    if current.get("is_super"):
        return "1=1", {}
    org_id = current.get("org_id")
    if org_id is None:
        raise HTTPException(403, {"message": "Sin contexto de organizacion."})
    placeholder = f"__org_id{param_suffix}"
    return f"{column} = :{placeholder}", {placeholder: org_id}
