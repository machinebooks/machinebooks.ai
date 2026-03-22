# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from fastapi import Depends, HTTPException, Request


class RequireModule:
    """Dependency de FastAPI que verifica que un módulo está
    licenciado para el tenant del usuario actual.

    Uso: @router.get("/dpia", dependencies=[Depends(RequireModule("privacy"))])
    """

    def __init__(self, module_code: str):
        self.module_code = module_code

    async def __call__(self, request: Request, db=Depends(get_db)):
        corporate_id = getattr(request.state, "corporate_id", None)
        if not corporate_id:
            raise HTTPException(status_code=401, detail="Tenant no identificado")

        # Consulta cacheada en Redis (TTL 15 min)
        license_entry = await get_module_license(
            corporate_id, self.module_code, db
        )

        if not license_entry or not license_entry.is_valid():
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Módulo '{self.module_code}' no está licenciado "
                    f"para su organización o la licencia ha expirado."
                )
            )
