# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
import bcrypt
import jwt
import redis
import pyotp
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

# Configuración centralizada
JWT_ALGORITHM = "RS256"  # HS256 solo en desarrollo
JWT_EXPIRATION_MINUTES = 60
JWT_ISSUER = "grc-platform"

redis_client = redis.Redis(host="redis", port=6379, db=1, decode_responses=True)


# --- Hashing de contraseñas ---

def hash_password(plain: str) -> str:
    """Genera hash bcrypt con factor de coste 12.
    Nunca almacenamos contraseñas en texto plano ni con algoritmos débiles."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Compara contraseña en texto plano contra hash almacenado.
    bcrypt gestiona internamente la extracción del salt."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# --- Generación y validación JWT ---

def create_access_token(
    user_id: int,
    corporate_id: int,
    roles: list[str],
    private_key: str,
    mfa_verified: bool = False,
) -> str:
    """Genera JWT firmado con RS256.
    Incluye JTI para revocación individual via blocklist."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "corporate_id": corporate_id,
        "roles": roles,
        "mfa_verified": mfa_verified,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "iss": JWT_ISSUER,
        "jti": str(uuid4()),  # Identificador único para blocklist
    }
    return jwt.encode(payload, private_key, algorithm=JWT_ALGORITHM)


def decode_token(token: str, public_key: str) -> dict:
    """Decodifica y valida JWT. Lanza excepción si ha expirado,
    la firma es inválida o el token está en blocklist."""
    payload = jwt.decode(
        token,
        public_key,
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
    )
    # Verificar blocklist en Redis
    if is_token_revoked(payload["jti"]):
        raise jwt.InvalidTokenError("Token revocado")
    return payload


# --- Blocklist JWT en Redis ---

def revoke_token(jti: str, exp_timestamp: float) -> None:
    """Añade JTI a la blocklist con TTL automático.
    Cuando el token habría expirado naturalmente, Redis elimina la entrada."""
    now = datetime.now(timezone.utc).timestamp()
    ttl_seconds = int(exp_timestamp - now)
    if ttl_seconds > 0:
        redis_client.setex(f"blocklist:{jti}", ttl_seconds, "revoked")


def is_token_revoked(jti: str) -> bool:
    """Consulta sub-milisegundo a Redis. Si Redis no está disponible,
    denegamos acceso por defecto (fail-closed)."""
    try:
        return redis_client.exists(f"blocklist:{jti}") > 0
    except redis.ConnectionError:
        # Fail-closed: si Redis cae, no validamos tokens
        return True
