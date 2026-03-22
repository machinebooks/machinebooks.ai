# Extraído de: LibroCISO/cap-01-ciso-ya-no-lee-pdfs.md
# Ejemplo didáctico: estructura base de una plataforma GRC con FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Plataforma GRC",
    version="1.0.0",
    docs_url=None,      # Swagger deshabilitado en producción
    redoc_url=None,      # ReDoc deshabilitado en producción
    openapi_url=None,    # Schema OpenAPI no expuesto públicamente
)

# Middleware stack ordenado — el orden importa:
# cada request atraviesa esta pila de arriba a abajo,
# cada response de abajo a arriba.
app.add_middleware(SecurityHeadersMiddleware)   # CSP, HSTS, X-Frame-Options
app.add_middleware(AuditMiddleware)             # Audit trail + CEF/Syslog → SIEM
app.add_middleware(TenantMiddleware)            # Aislamiento multi-tenant
app.add_middleware(RateLimitMiddleware)         # Auth: 10/min, AI: 20/h
app.add_middleware(RequestIDMiddleware)         # Trazabilidad con X-Request-ID

# 30+ routers por dominio regulatorio
app.include_router(privacy_router, prefix="/api/v1/privacy")
app.include_router(risk_router, prefix="/api/v1/risk")
app.include_router(compliance_router, prefix="/api/v1/compliance")
app.include_router(nis2_router, prefix="/api/v1/nis2")
app.include_router(dora_router, prefix="/api/v1/dora")
app.include_router(ai_router, prefix="/api/v1/ai")
app.include_router(agents_router, prefix="/api/v1/agents")
