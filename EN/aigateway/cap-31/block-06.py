# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Role-based authorization — gateway/app/api/v1/compliance_portal.py:88-101
async def require_compliance(request: Request) -> dict:
    auth = await validate_auth(request)
    role = auth.get("role", "")
    if role not in ("compliance_champion", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "compliance_forbidden_role",
                "message": "Acceso restringido al portal de cumplimiento.",
            },
        )
