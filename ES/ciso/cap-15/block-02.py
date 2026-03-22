# Extraído de: LibroCISO/cap-15-autenticacion-capas.md
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])


class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: Optional[str] = None
    auth_method: str = "local"  # "local" | "ldap"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: bool = False


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    """Login unificado que soporta autenticación local y LDAP.

    Flujo:
    1. Autenticar credenciales (local o LDAP)
    2. Si el usuario tiene MFA activado y no envía código → mfa_required=True
    3. Si envía código MFA → verificar TOTP
    4. Generar JWT con claims completos
    """
    # Paso 1: verificar credenciales según método
    if request.auth_method == "ldap":
        user = await authenticate_ldap(request.username, request.password, db)
    else:
        user = await authenticate_local(request.username, request.password, db)

    if not user:
        # Mensaje genérico para no revelar si el usuario existe
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Paso 2: verificar si MFA es obligatorio
    mfa_required = user_requires_mfa(user)
    mfa_verified = False

    if mfa_required:
        if not request.mfa_code:
            # El cliente debe repetir la petición con el código TOTP
            return LoginResponse(
                access_token="",
                expires_in=0,
                mfa_required=True,
            )
        # Paso 3: verificar código TOTP
        if not verify_totp(user.mfa_secret, request.mfa_code):
            raise HTTPException(status_code=401, detail="Código MFA inválido")
        mfa_verified = True

    # Paso 4: generar JWT
    token = create_access_token(
        user_id=user.id,
        corporate_id=user.corporate_id,
        roles=[r.name for r in user.roles],
        private_key=get_private_key(),
        mfa_verified=mfa_verified,
    )

    # Registrar login exitoso en audit trail
    await log_audit_event(
        action="LOGIN",
        user_id=user.id,
        corporate_id=user.corporate_id,
        details={
            "method": request.auth_method,
            "mfa": mfa_verified,
            "ip": request.client.host,
        },
    )

    return LoginResponse(
        access_token=token,
        expires_in=JWT_EXPIRATION_MINUTES * 60,
        mfa_required=False,
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(authenticate_request)):
    """Revoca el token actual añadiéndolo a la blocklist Redis."""
    token = get_current_token()
    payload = jwt.decode(token, options={"verify_signature": False})
    revoke_token(payload["jti"], payload["exp"])

    await log_audit_event(
        action="LOGOUT",
        user_id=current_user["user_id"],
        corporate_id=current_user["corporate_id"],
    )
    return {"detail": "Sesión cerrada"}
