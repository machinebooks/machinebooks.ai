# Chapter 16 — TenantMiddleware: corporate_id injection from JWT
#
# Extracts the corporate_id from the authenticated user's JWT claims
# and injects it into request.state. Every downstream service and
# repository uses this value to filter data by tenant.
#
# The developer CANNOT forget the tenant filter — if an endpoint
# tries to query without corporate_id, the repository raises an error.

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class TenantMiddleware(BaseHTTPMiddleware):
    """Extracts corporate_id from the authenticated user and injects it
    into request.state for the entire processing chain.

    Runs AFTER authentication middleware (JWT verification) and BEFORE
    any business logic endpoint.

    Routes in EXEMPT_PATHS do not require a tenant (login, health, docs).
    """

    EXEMPT_PATHS = {"/api/v1/auth/login", "/health", "/docs", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        # Exempt routes do not need a tenant
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Extract claims from JWT (already verified by AuthMiddleware)
        claims = getattr(request.state, "user_claims", None)
        if not claims:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token does not contain user claims"},
            )

        corporate_id = claims.get("corporate_id")
        if not corporate_id:
            return JSONResponse(
                status_code=403,
                content={"detail": "User has no assigned tenant"},
            )

        # Inject into request.state — available to the entire chain
        request.state.corporate_id = corporate_id
        request.state.user_id = claims.get("user_id")
        request.state.role = claims.get("role")

        return await call_next(request)
