# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Creación del token JWT con session identifier
# Fichero: cyber-range-builder/backend/auth/__init__.py

ALG = "HS256"

def create_token(user: User):
    """Genera un JWT con claims del usuario y session ID.
    El campo 'sid' permite invalidar tokens en logout
    sin necesidad de mantener una blacklist."""
    exp = datetime.utcnow() + timedelta(hours=settings.jwt_exp_hours)  # 4h
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,       # admin, red, blue, purple, organizer, viewer
        "exp": exp
    }
    # El session_token vincula el JWT con la sesión activa en BD
    if user.session_token:
        payload["sid"] = user.session_token
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALG)
