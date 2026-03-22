# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Verificación de rol como dependencia de FastAPI
# Fichero: cyber-range-builder/backend/auth/__init__.py

def role_required(*roles):
    """Decorador que restringe el acceso a los roles especificados.
    Se aplica como dependencia de FastAPI en cada endpoint."""
    async def checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role"
            )
        return user
    return checker

# Uso en endpoints — cada router declara qué roles pueden acceder:
# router = APIRouter(dependencies=[Depends(role_required("admin"))])
# O por endpoint individual:
# @router.get("/scenarios", dependencies=[Depends(role_required("admin", "organizer"))])
