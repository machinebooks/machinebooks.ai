# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/scim.py — SCIM user creation
@router.post("/Users", status_code=201)
async def create_user(payload, db, authorization):
    cfg = await _require_scim(db, authorization)
    user_name = (payload.get("userName") or "").strip().lower()
    if not user_name or "@" not in user_name:
        raise _scim_error(400, "userName with email is required")
    full_name = _split_name(payload) or user_name
    active = bool(payload.get("active", True))

    # 409 if already exists
    exists = await db.execute(sa_text(
        "SELECT id FROM users WHERE email = :e LIMIT 1"
    ), {"e": user_name})
    if exists.first():
        raise _scim_error(409, f"user with userName={user_name} already exists")

    # INSERT with password_hash NULL (SSO only).
    # org_id comes from the resolved SCIM config, never hardcoded.
    res = await db.execute(sa_text("""
        INSERT INTO users (organization_id, email, name, role,
                           is_active, team_id, created_at, updated_at)
        VALUES (:org, :email, :name, 'user', :active, :team, NOW(), NOW())
    """), {"org": cfg["organization_id"], "email": user_name,
           "name": full_name, "active": 1 if active else 0,
           "team": cfg.get("default_team_id")})
    await db.commit()
