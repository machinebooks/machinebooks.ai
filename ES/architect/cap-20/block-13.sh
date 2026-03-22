# Extraído de: LibroTecnico/cap-20-docker.md
# --- SEGURIDAD ---
SECRET_KEY=<set-in-vault>
# Generar con: python -c "import secrets; print(secrets.token_hex(64))"
# OBLIGATORIO — la aplicación falla al arrancar si no está definida
JWT_SECRET_KEY=<set-in-vault>
JWT_ACCESS_TOKEN_EXPIRES=3600     # 1 hora
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 días
FERNET_KEY=<clave-fernet-para-cifrado-MFA>

# API Keys internas entre servicios (no expuestas al exterior)
INTERNAL_API_KEY_OPS=<clave-random-para-app-operacional>
INTERNAL_API_KEY_ANALYTICS=<clave-random-para-app-analytics>
INTERNAL_API_KEY_ADMIN=<clave-random-para-app-admin>
AI_SERVICE_API_KEY=<clave-interna-backend-a-ai-service>

# --- SELENIUM ---
SELENIUM_HUB_URL=http://selenium_hub:4444/wd/hub
SELENIUM_TIMEOUT_IMPLICIT=10
SELENIUM_TIMEOUT_PAGE_LOAD=30
SELENIUM_TIMEOUT_SCRIPT=30

# --- EMAIL (SMTP para OTP y notificaciones) ---
SMTP_HOST=smtp.ejemplo.com
SMTP_PORT=587
SMTP_USER=sistema@ejemplo.com
SMTP_PASSWORD=<contraseña-smtp>
SMTP_USE_TLS=true
EMAIL_FROM=sistema@ejemplo.com

# --- LOGGING Y OBSERVABILIDAD ---
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=<dsn-si-se-usa-sentry>
ENABLE_AUDIT_LOG=true
AUDIT_LOG_RETENTION_DAYS=365

# --- GDPR Y COMPLIANCE ---
DATA_RETENTION_DAYS=730
PII_DETECTION_ENABLED=true
GDPR_CONSENT_REQUIRED=true
AI_COMPLIANCE_CHECK_INTERVAL_HOURS=6

# --- INTEGRACIÓN CRM ---
CRM_BASE_URL=https://api.ejemplo.com/crm
CRM_OAUTH_CLIENT_ID=<client-id>
CRM_OAUTH_CLIENT_SECRET=<client-secret>
CRM_SYNC_INTERVAL_MINUTES=5

# --- CONFIGURACIÓN DE APLICACIÓN ---
MAX_UPLOAD_SIZE_MB=100
MAX_PDF_PAGES=500
AI_DEFAULT_MAX_TOKENS=4096
AI_STREAMING_ENABLED=true
RAG_TOP_K=5
RAG_SCORE_THRESHOLD=0.7
ALERT_SCORE_THRESHOLD=7.0    # Umbral para alertas proactivas de oportunidades
