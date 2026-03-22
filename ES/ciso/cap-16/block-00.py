# Extraído de: LibroCISO/cap-16-rbac-multitenancy.md
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.auth.jwt_utils import get_current_user_claims


class TenantMiddleware(BaseHTTPMiddleware):
    """Extrae corporate_id del usuario autenticado y lo inyecta
    en request.state para que toda la cadena de procesamiento
    tenga acceso al tenant sin depender de parámetros manuales."""

    # Rutas que no requieren tenant (login, health, docs)
    EXEMPT_PATHS = {"/api/v1/auth/login", "/health", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        # Rutas exentas no necesitan tenant
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Extraer claims del JWT (ya verificado por AuthMiddleware)
        claims = getattr(request.state, "user_claims", None)
        if not claims:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token no contiene claims de usuario"}
            )

        corporate_id = claims.get("corporate_id")
        if not corporate_id:
            return JSONResponse(
                status_code=403,
                content={"detail": "Usuario sin tenant asignado"}
            )

        # Inyectar en request.state — disponible para toda la cadena
        request.state.corporate_id = corporate_id
        request.state.user_id = claims.get("user_id")
        request.state.role = claims.get("role")

        return await call_next(request)
