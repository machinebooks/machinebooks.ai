# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/sso.py — creación automática de usuario SSO
if not user:
    # Cross-org check con mensaje uniforme (anti-enumeración)
    exists_anywhere = await db.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    user_other_org = exists_anywhere.scalar_one_or_none()
    if user_other_org and user_other_org.organization_id != org.id:
        raise HTTPException(403, "No autorizado")  # mensaje genérico

    user = User(
        email=email, name=name,
        password_hash=hash_password(secrets.token_urlsafe(32)),  # sin login local
        role="viewer", is_active=True, mfa_enabled=False,
        organization_id=org.id, auth_source="sso",
    )
    db.add(user)
    await db.commit()
