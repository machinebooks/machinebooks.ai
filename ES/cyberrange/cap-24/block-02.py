# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Bloqueo por intentos fallidos con clave compuesta ip:username
# Fichero: cyber-range-builder/backend/auth/__init__.py

def _lockout_key(ip: str, username: str) -> str:
    """Clave compuesta ip:username para prevenir DoS por bloqueo."""
    return f"{ip}:{username}"

def check_account_lockout(user: User, request: Request):
    """Verifica si el par IP-usuario está bloqueado."""
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cuenta bloqueada. Intente de nuevo en {remaining + 1} minutos."
        )

def record_failed_login(user: User, request: Request, db: Session):
    """Registra intento fallido con clave compuesta ip:username."""
    key = _lockout_key(request.client.host, user.email)
    user.failed_login_count = (user.failed_login_count or 0) + 1
    if user.failed_login_count >= settings.max_failed_logins:  # 5 intentos
        user.locked_until = datetime.utcnow() + timedelta(
            minutes=settings.account_lockout_minutes  # 30 minutos
        )
        logger.warning(
            f"Account locked: {key} "
            f"after {user.failed_login_count} failed attempts"
        )
    db.commit()
