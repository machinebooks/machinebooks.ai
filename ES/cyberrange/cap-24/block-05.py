# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Verificación completa del token JWT
# Fichero: cyber-range-builder/backend/auth/__init__.py

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Obtiene el usuario actual verificando el JWT contra la base de datos.
    No confía solo en los claims del token — verifica todo contra BD."""

    # 1. Verificar que existe el header Authorization con formato Bearer
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    # 2. Validar formato del token (3 partes separadas por puntos)
    auth_parts = auth.split()
    if len(auth_parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización inválido"
        )
    token = auth_parts[1]
    token_parts = token.split('.')
    if len(token_parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido"
        )

    # 3. Decodificar y verificar firma + expiración
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # 4. Verificar que el usuario existe y está activo
    user_id = int(payload["sub"])
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada"
        )

    # 5. Verificar que la sesión no fue invalidada
    #    (logout desde otro dispositivo, acción de admin, etc.)
    token_sid = payload.get("sid")
    if user.session_token and token_sid and token_sid != user.session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión invalidada"
        )

    # 6. Inyectar usuario verificado en el contexto de la petición
    request.state.user = user
    return user
