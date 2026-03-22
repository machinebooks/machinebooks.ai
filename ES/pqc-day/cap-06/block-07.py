# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# Ejemplo didáctico: patrones/app/__init__.py — Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,       # Limitar por IP de origen
    storage_uri=app.config['RATELIMIT_STORAGE_URL']  # Redis
)
