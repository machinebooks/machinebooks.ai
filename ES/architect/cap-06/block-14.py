# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
# Configuración en ai_service (FastAPI) — claves desde variables de entorno
VALID_API_KEYS = {
    os.environ['API_KEY_OPS']:       {"app": "operations", "max_tokens": 4096},
    os.environ['API_KEY_ANALYTICS']: {"app": "analytics",  "max_tokens": 8192},
    os.environ['API_KEY_ADMIN']:     {"app": "admin",       "max_tokens": 16384},
}

async def verify_internal_api_key(request: Request):
    """Verifica API key interna y extrae contexto de aplicación."""
    api_key = (request.headers.get('X-Internal-API-Key-Ops') or
               request.headers.get('X-Internal-API-Key-Analytics') or
               request.headers.get('X-Internal-API-Key-Admin'))

    if not api_key:
        raise HTTPException(status_code=401, detail="API key requerida")

    # Comparación timing-safe para prevenir ataques de temporización
    # Se itera sobre TODAS las entradas sin break para evitar timing attacks
    matched_config = None
    for valid_key, config in VALID_API_KEYS.items():
        if hmac.compare_digest(api_key.encode(), valid_key.encode()):
            matched_config = config

    if not matched_config:
        audit_log('ACCESS_DENIED', severity='WARNING',
                 details=f"API key inválida desde {request.client.host}")
        raise HTTPException(status_code=401, detail="API key inválida")

    return matched_config
