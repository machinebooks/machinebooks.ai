# Extracted from: LibroAIGateway/cap-30-user-portal.md
# gateway/app/api/v1/me.py — disable TOTP
@router.delete("/mfa/totp")
@limiter.limit("10/minute")
async def totp_disable(request, body: TotpVerifyRequest, db):
    user = await _current_user(request, db)
    if not TotpService.verify(user.mfa_secret, body.code):
        raise HTTPException(401, "Incorrect TOTP code")
    user.mfa_secret = None
    # mfa_enabled = True: falls back to email MFA, never to zero
    await db.commit()
    await SecurityEventService.emit(db, "mfa_totp_disabled", "warning", ...)
