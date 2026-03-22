# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
# La clave privada actual firma nuevos tokens.
# La clave pública actual Y la anterior verifican tokens existentes.
# Esto permite una ventana de transición: los tokens firmados con la
# clave anterior siguen siendo válidos hasta que expiran naturalmente.

JWT_CURRENT_KEY_ID = os.environ.get("JWT_CURRENT_KEY_ID", "key-2025-01")
JWT_PRIVATE_KEY = load_private_key(os.environ["JWT_PRIVATE_KEY_PATH"])
JWT_PUBLIC_KEYS = {
    "key-2025-01": load_public_key("/etc/ssl/jwt/key-2025-01.pub"),
    "key-2024-07": load_public_key("/etc/ssl/jwt/key-2024-07.pub"),  # Anterior
}


def create_access_token_with_kid(user_id, corporate_id, roles, mfa_verified):
    """Incluye 'kid' (Key ID) en el header JWT para que el verificador
    sepa qué clave pública usar."""
    headers = {"kid": JWT_CURRENT_KEY_ID}
    payload = {
        "sub": str(user_id),
        "corporate_id": corporate_id,
        "roles": roles,
        "mfa_verified": mfa_verified,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, JWT_PRIVATE_KEY, algorithm="RS256", headers=headers)


def decode_token_with_kid(token: str) -> dict:
    """Selecciona la clave pública correcta usando el 'kid' del header."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    public_key = JWT_PUBLIC_KEYS.get(kid)
    if not public_key:
        raise jwt.InvalidTokenError(f"Key ID desconocido: {kid}")
    return jwt.decode(token, public_key, algorithms=["RS256"])
