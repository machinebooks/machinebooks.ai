# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from datetime import datetime, timezone

# Límites configurables por entorno
MAX_ATTEMPTS_PER_IP = int(os.environ.get("LOGIN_MAX_ATTEMPTS_IP", "20"))
MAX_ATTEMPTS_PER_USER = int(os.environ.get("LOGIN_MAX_ATTEMPTS_USER", "5"))
LOCKOUT_MINUTES = int(os.environ.get("LOGIN_LOCKOUT_MINUTES", "15"))


async def check_login_rate_limit(username: str, client_ip: str) -> None:
    """Verifica rate limits antes de intentar autenticación.
    Dos niveles: por IP (protege contra barrido de cuentas)
    y por usuario (protege contra fuerza bruta dirigida)."""

    # Nivel 1: límite por IP — evita que una IP pruebe muchas cuentas
    ip_key = f"login_attempts:ip:{client_ip}"
    ip_attempts = int(redis_client.get(ip_key) or 0)
    if ip_attempts >= MAX_ATTEMPTS_PER_IP:
        await log_audit_event(
            action="LOGIN_RATE_LIMITED",
            details={"reason": "ip_limit", "ip": client_ip},
        )
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Reintente en unos minutos.",
        )

    # Nivel 2: límite por usuario — evita fuerza bruta contra una cuenta
    user_key = f"login_attempts:user:{username}"
    user_attempts = int(redis_client.get(user_key) or 0)
    if user_attempts >= MAX_ATTEMPTS_PER_USER:
        await log_audit_event(
            action="LOGIN_RATE_LIMITED",
            details={"reason": "user_limit", "username": username},
        )
        raise HTTPException(
            status_code=429,
            detail="Cuenta bloqueada temporalmente por intentos fallidos.",
        )


async def record_failed_attempt(username: str, client_ip: str) -> None:
    """Registra intento fallido en ambos contadores con TTL."""
    ip_key = f"login_attempts:ip:{client_ip}"
    user_key = f"login_attempts:user:{username}"

    pipe = redis_client.pipeline()
    pipe.incr(ip_key)
    pipe.expire(ip_key, LOCKOUT_MINUTES * 60)
    pipe.incr(user_key)
    pipe.expire(user_key, LOCKOUT_MINUTES * 60)
    pipe.execute()


async def clear_failed_attempts(username: str, client_ip: str) -> None:
    """Limpia contadores tras login exitoso."""
    redis_client.delete(f"login_attempts:ip:{client_ip}")
    redis_client.delete(f"login_attempts:user:{username}")
