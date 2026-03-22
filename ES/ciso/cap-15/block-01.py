# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

bearer_scheme = HTTPBearer(auto_error=False)


async def authenticate_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """Middleware que detecta el método de autenticación por los headers.

    Orden de prioridad:
    1. Certificado X.509 (mTLS) — header X-Client-Cert de Nginx
    2. SAML assertion — cookie de sesión SAML
    3. JWT Bearer — header Authorization: Bearer <token>

    Si ninguno está presente, rechaza con 401."""

    # 1. PKI/mTLS: Nginx pasa el certificado como header
    client_cert = request.headers.get("X-Client-Cert")
    client_verify = request.headers.get("X-Client-Verify")
    if client_cert and client_verify == "SUCCESS":
        return await authenticate_pki(client_cert)

    # 2. SAML: sesión establecida por el flujo SSO
    saml_session = request.cookies.get("saml_session_id")
    if saml_session:
        return await authenticate_saml_session(saml_session)

    # 3. JWT: el método estándar
    if credentials and credentials.scheme == "Bearer":
        return await authenticate_jwt(credentials.credentials)

    raise HTTPException(
        status_code=401,
        detail="No se encontró credencial válida",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authenticate_jwt(token: str) -> dict:
    """Valida JWT y devuelve el payload con datos del usuario."""
    try:
        payload = decode_token(token, get_public_key())
        return {
            "user_id": int(payload["sub"]),
            "corporate_id": payload["corporate_id"],
            "roles": payload["roles"],
            "mfa_verified": payload.get("mfa_verified", False),
            "auth_method": "jwt",
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")


async def authenticate_pki(cert_pem: str) -> dict:
    """Extrae identidad del certificado X.509 y busca usuario en BD."""
    cert_info = parse_x509_certificate(cert_pem)

    # Verificar cadena de confianza y revocación
    if not verify_certificate_chain(cert_info):
        raise HTTPException(status_code=401, detail="Certificado no confiable")

    if is_certificate_revoked(cert_info):
        raise HTTPException(status_code=401, detail="Certificado revocado")

    # Buscar usuario por CN o campo personalizado del certificado
    user = await find_user_by_certificate(cert_info["subject_cn"])
    if not user:
        raise HTTPException(status_code=403, detail="Certificado válido, usuario no registrado")

    return {
        "user_id": user.id,
        "corporate_id": user.corporate_id,
        "roles": [r.name for r in user.roles],
        "mfa_verified": True,  # PKI implica factor fuerte
        "auth_method": "pki",
    }
