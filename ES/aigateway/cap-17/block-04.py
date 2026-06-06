# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/sso_service.py — derivación automática de JWKS
def _derive_jwks_uri(config: dict) -> str:
    provider = (config.get("provider") or "").lower()
    if provider == "azure_ad" and config.get("tenant_id"):
        return f"https://login.microsoftonline.com/{config['tenant_id']}/discovery/v2.0/keys"
    if provider == "google":
        return "https://www.googleapis.com/oauth2/v3/certs"
    if provider == "okta" and config.get("domain"):
        return f"https://{config['domain']}.okta.com/oauth2/default/v1/keys"
    # Fallback OIDC genérico: issuer/.well-known/jwks.json
    issuer = config.get("issuer") or ""
    return (issuer.rstrip("/") + "/.well-known/jwks.json") if issuer else ""
