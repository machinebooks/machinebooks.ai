# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/sso.py — punto de entrada SSO
@router.get("/{org_slug}/login")
@limiter.limit("20/minute")
async def sso_login(
    request: Request,
    org_slug: str,
    redirect_uri: str = "https://app.ejemplo.com/sso/callback",
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    org = await db.get(Organization, org_slug)
    if not org or not SSOService.is_enabled(org):
        raise HTTPException(400, "SSO no habilitado")

    if redirect_uri not in ALLOWED_REDIRECT_URIS:
        raise HTTPException(400, "redirect_uri no permitido")

    state = secrets.token_urlsafe(32)  # CSRF
    nonce = secrets.token_urlsafe(32)  # replay
    await redis.setex(f"n7x:sso:state:{state}", 300,
        json.dumps({"org_id": org.id, "org_slug": org_slug,
                     "redirect_uri": redirect_uri, "nonce": nonce}))

    auth_url = SSOService.get_authorization_url(org, redirect_uri, state, nonce)
    return RedirectResponse(auth_url)
