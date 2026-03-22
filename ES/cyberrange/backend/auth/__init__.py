# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/auth/__init__.py — Fábrica de dependencias de rol
def role_required(*roles):
    """Genera una dependencia que verifica que el usuario tiene uno de los roles indicados."""
    async def checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient role"
            )
        return user
    return checker
