# Extraído de: LibroCISO/cap-01-ciso-ya-no-lee-pdfs.md
# Ejemplo didáctico: router de privacidad con control de acceso por rol
from fastapi import APIRouter, Depends

privacy_router = APIRouter(tags=["privacy"])

@privacy_router.get("/treatments")
async def list_treatments(
    current_user=Depends(get_current_user),
    _=Depends(require_permission("privacy.treatments.read")),
    tenant=Depends(get_current_tenant),
):
    """
    Lista los tratamientos de datos del tenant actual.
    El permiso privacy.treatments.read es obligatorio.
    El filtro por tenant es automático — nunca se sirven
    datos de una organización a otra.
    """
    return await treatment_service.list_by_tenant(tenant.id)
