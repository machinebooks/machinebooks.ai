# Extraído de: LibroCISO/cap-17-hardening-siem.md
# Ejemplo didáctico: app/main.py — registro de middleware

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.audit import AuditMiddleware
from app.middleware.tenant import TenantMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="GRC Platform", version="1.0.0")

# IMPORTANTE: el orden de add_middleware es INVERSO al de ejecución.
# El último registrado se ejecuta primero.
# Orden de ejecución deseado:
#   SecurityHeaders → Audit → Tenant → RateLimit → RequestID → GZip → CORS

# 7. CORS — se ejecuta último (más interno)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://grc.ejemplo.com"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 6. GZip — compresión de respuestas
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. RequestID — genera o propaga X-Request-ID
app.add_middleware(RequestIDMiddleware)

# 4. RateLimit — límites diferenciados por categoría
app.add_middleware(RateLimitMiddleware)

# 3. Tenant — extrae corporate_id del JWT
app.add_middleware(TenantMiddleware)

# 2. Audit — registra operaciones mutantes (necesita tenant y request_id)
app.add_middleware(AuditMiddleware)

# 1. SecurityHeaders — se ejecuta primero (más externo)
app.add_middleware(SecurityHeadersMiddleware)
