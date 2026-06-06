# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/api/v1/scim.py — SCIM auth with hashed bearer
async def _require_scim(db, authorization):
    cfg = await _load_scim_config(db)
    if not cfg["enabled"]:
        raise HTTPException(503, "SCIM not enabled")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "bearer token required")
    token = authorization.split(" ", 1)[1].strip()
    h = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if h != cfg["bearer_token_hash"]:
        raise HTTPException(401, "invalid bearer token")
    return cfg
