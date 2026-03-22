# Extraído de: LibroTecnico/cap-20-docker.md
# --- SERVICIOS IA ---
# Claude (Anthropic) — proveedor principal
ANTHROPIC_API_KEY=<sk-ant-...>

# Azure OpenAI — proveedor de respaldo
AZURE_OPENAI_API_KEY=<clave-azure>
AZURE_OPENAI_ENDPOINT=https://api.ejemplo.com/openai/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_GPT4=gpt-4o
AZURE_OPENAI_DEPLOYMENT_ADA=text-embedding-3-large

# OpenAI directo — proveedor terciario
OPENAI_API_KEY=<sk-...>

# Modelos Anthropic por defecto (sobrescribibles desde Admin)
DEFAULT_MODEL_HEAVY=claude-opus-4-6
DEFAULT_MODEL_STANDARD=claude-sonnet-4-6
DEFAULT_MODEL_FAST=claude-haiku-4-5

# --- SERVICIOS VECTORIALES Y DE BÚSQUEDA ---
QDRANT_HOST=qdrant
QDRANT_PORT=6333
# Generar con: openssl rand -base64 32
QDRANT_API_KEY=<set-in-vault>

MEILISEARCH_HOST=http://meilisearch:7700
MEILISEARCH_API_KEY=<set-in-vault>
MEILISEARCH_INDEX_MEMORY=512Mb

# --- REDIS Y CELERY ---
# Generar con: openssl rand -base64 32
REDIS_PASSWORD=<set-in-vault>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/2
# Límite de tasa por tipo de tarea
CELERY_RATE_LIMIT_AI=30/m
CELERY_RATE_LIMIT_AUTOMATION=5/m
CELERY_RATE_LIMIT_DOCUMENTS=10/m

