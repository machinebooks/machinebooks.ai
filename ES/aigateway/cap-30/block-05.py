# Extraído de: LibroAIGateway/cap-30-portal-usuario.md
# gateway/app/api/v1/me.py — disable TOTP
@router.delete("/mfa/totp")
@limiter.limit("10/minute")
async def totp_disable(request, body: TotpVerifyRequest, db):
    user = await _current_user(request, db)
    if not TotpService.verify(user.mfa_secret, body.code):
        raise HTTPException(401, "Código TOTP incorrecto")
    user.mfa_secret = None
    # mfa_enabled = True: cae a email MFA, nunca a zero
    await db.commit()
    await SecurityEventService.emit(db, "mfa_totp_disabled", "warning", ...)
