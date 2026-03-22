# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Autenticación de WebSocket via JWT
# Fichero: cyber-range-builder/backend/routers/gaming.py

def get_current_user_from_auth(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Extrae y verifica el usuario desde el header Authorization.
    Usado tanto en REST como en el handshake de WebSocket."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Usuario no autenticado")

    token = authorization.split()[1]
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=["HS256"]
        )
        user_id = int(payload["sub"])
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
