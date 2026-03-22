# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from fastapi import Depends, HTTPException, Request
from typing import Callable


def require_permission(module: str, action: str) -> Callable:
    """Dependency de FastAPI que verifica permisos por rol.

    Uso: @router.get("/risks", dependencies=[Depends(require_permission("risk", "read"))])

    Verifica:
    1. Usuario autenticado (request.state.user_id existe)
    2. Rol del usuario tiene permiso module:action
    3. Módulo está licenciado para el tenant
    """

    async def _check_permission(request: Request, db=Depends(get_db)):
        user_id = getattr(request.state, "user_id", None)
        corporate_id = getattr(request.state, "corporate_id", None)
        role = getattr(request.state, "role", None)

        if not user_id or not corporate_id or not role:
            raise HTTPException(status_code=401, detail="No autenticado")

        # Verificar permiso del rol
        # Los permisos se cachean en Redis (TTL 5 min) para evitar
        # una query a BD en cada petición
        permissions = await get_role_permissions(role, corporate_id, db)

        module_perms = permissions.get(module, [])
        if action not in module_perms:
            raise HTTPException(
                status_code=403,
                detail=f"Rol '{role}' no tiene permiso '{module}:{action}'"
            )

        # Verificar licencia del módulo para el tenant
        if not await is_module_licensed(corporate_id, module, db):
            raise HTTPException(
                status_code=403,
                detail=f"Módulo '{module}' no licenciado para este tenant"
            )

    return _check_permission
