# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/scim.py — creación de usuario SCIM
@router.post("/Users", status_code=201)
async def create_user(payload, db, authorization):
    cfg = await _require_scim(db, authorization)
    user_name = (payload.get("userName") or "").strip().lower()
    if not user_name or "@" not in user_name:
        raise _scim_error(400, "userName con email es obligatorio")
    full_name = _split_name(payload) or user_name
    active = bool(payload.get("active", True))

    # 409 si ya existe
    exists = await db.execute(sa_text(
        "SELECT id FROM users WHERE email = :e LIMIT 1"
    ), {"e": user_name})
    if exists.first():
        raise _scim_error(409, f"user con userName={user_name} ya existe")

    # INSERT con password_hash NULL (solo SSO).
    # org_id sale de la configuración SCIM resuelta, nunca hardcodeado.
    res = await db.execute(sa_text("""
        INSERT INTO users (organization_id, email, name, role,
                           is_active, team_id, created_at, updated_at)
        VALUES (:org, :email, :name, 'user', :active, :team, NOW(), NOW())
    """), {"org": cfg["organization_id"], "email": user_name,
           "name": full_name, "active": 1 if active else 0,
           "team": cfg.get("default_team_id")})
    await db.commit()
