# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/sso_service.py — verificación del id_token
@classmethod
async def verify_id_token(cls, org, id_token, expected_nonce=None):
    config = cls.get_config(org)
    jwks_uri = config.get("jwks_uri") or _derive_jwks_uri(config)
    expected_iss = config.get("issuer") or _derive_issuer(config)
    expected_aud = config.get("client_id")

    # Fetch JWKS del IdP (con SSRF guard + follow_redirects=False)
    async with httpx.AsyncClient(follow_redirects=False, timeout=10.0) as client:
        jwks_resp = await client.get(jwks_uri)
        jwks = jwks_resp.json()

    # Verificar firma + iss + aud + exp
    key = JsonWebKey.import_key_set(jwks)
    claims = authlib_jwt.decode(
        id_token, key,
        claims_options={
            "iss": {"essential": True, "value": expected_iss},
            "aud": {"essential": True, "value": expected_aud},
            "exp": {"essential": True},
        },
    )
    claims.validate()  # valida exp/nbf
    return dict(claims)
