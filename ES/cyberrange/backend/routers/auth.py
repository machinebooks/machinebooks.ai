# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/auth.py — Login con todas las protecciones
class LoginIn(BaseModel):
    email: str
    password: str
    mfa_code: Optional[str] = None

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mfa_required: bool = False

@router.post("/login", response_model=TokenOut)
def login(creds: LoginIn, db: Session = Depends(get_db)):
    # 1. Buscar usuario por email
    user = db.query(User).filter_by(email=creds.email).first()

    # 2. Verificar credenciales
    if not user or not verify_password(creds.password, user.hashed_pw):
        if user:
            record_failed_login(user, db)  # Incrementar contador
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # 3. Verificar bloqueo de cuenta
    check_account_lockout(user)

    # 4. Verificar que la cuenta está activa
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    # 5. Verificar MFA si está habilitado
    if user.mfa_enabled:
        if not creds.mfa_code:
            # Indicar al frontend que debe solicitar el código MFA
            return {"access_token": "", "token_type": "bearer", "mfa_required": True}
        if not verify_mfa_code(user.mfa_secret, creds.mfa_code):
            record_failed_login(user, db)
            raise HTTPException(status_code=401, detail="Código MFA inválido")

    # 6. Generar session token para gestión de sesiones
    user.session_token = secrets.token_hex(32)
    record_successful_login(user, db)

    # 7. Emitir JWT
    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "mfa_required": False
    }
