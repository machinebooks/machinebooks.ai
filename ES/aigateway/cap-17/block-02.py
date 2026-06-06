# Extraído de: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/sso_service.py — guard SSRF en endpoints SSO
def _validate_sso_endpoint(url: str, label: str) -> None:
    """Valida un endpoint SSO antes de hacer la petición HTTP."""
    if not url:
        raise ValueError(f"{label} no configurado")
    if settings.is_production:
        scheme = (urlparse(url).scheme or "").lower()
        if scheme != "https":
            raise ValueError(f"{label} debe usar https en producción")
    try:
        validate_outbound_url(url)  # bloquea localhost/IP privada
    except HTTPException as exc:
        raise ValueError(f"{label} inválido: {exc.detail}")
