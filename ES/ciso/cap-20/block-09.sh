# Extraído de: LibroCISO/cap-20-docker-compose.md
# .env.prod — Ejemplo de estructura (valores reales NUNCA en documentación)
# Base de datos
DB_ROOT_PASS=<contraseña-32-caracteres-aleatorios>
DB_PASS=<contraseña-32-caracteres-aleatorios>
DB_HOST=mysql
DB_NAME=grc_db

# Redis
REDIS_PASS=<contraseña-32-caracteres-aleatorios>

# JWT y autenticación
JWT_SECRET=<secreto-64-caracteres-aleatorios>
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=8

# IA
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=<set-in-vault>

# Ollama (entornos sin internet)
OLLAMA_BASE_URL=http://ollama:11434

# Cifrado de datos en reposo (AES-256-GCM)
ENCRYPTION_KEY=<clave-256-bits-base64>

# Grafana
GRAFANA_PASS=<contraseña-admin-grafana>

# Configuración general
ENVIRONMENT=production
LOG_LEVEL=WARNING
GRC_DOMAIN=grc.entidad.local
GUNICORN_WORKERS=4
CELERY_CONCURRENCY=4
