# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def configure_zap_auth(security_schemes: dict, target_url: str) -> dict:
    """Genera configuración de autenticación de ZAP según los esquemas OpenAPI."""
    auth_config = {}

    for scheme_name, scheme in security_schemes.items():
        if scheme["type"] == "http" and scheme["scheme"] == "bearer":
            auth_config = {
                "method": "json",
                "login_url": f"{target_url}/auth/login",
                "token_extraction": "$.access_token",
                "header_name": "Authorization",
                "header_prefix": "Bearer ",
                "token_refresh_url": f"{target_url}/auth/refresh",
                "token_ttl_seconds": 3600,
            }
        elif scheme["type"] == "apiKey":
            auth_config = {
                "method": "header",
                "header_name": scheme.get("name", "X-API-Key"),
                "header_value": "${API_KEY_FOR_DAST}",
            }
        elif scheme["type"] == "oauth2":
            flows = scheme.get("flows", {})
            if "clientCredentials" in flows:
                auth_config = {
                    "method": "oauth2_client_credentials",
                    "token_url": flows["clientCredentials"]["tokenUrl"],
                    "client_id": "${OAUTH_CLIENT_ID}",
                    "client_secret": "${OAUTH_CLIENT_SECRET}",
                    "scopes": list(flows["clientCredentials"]
                                   .get("scopes", {}).keys()),
                }

    return auth_config
