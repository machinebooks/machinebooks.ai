# Extracted from: LibroAIGateway/cap-17-sso-scim-mfa.md
# gateway/app/services/sso_service.py — SSRF guard on SSO endpoints
def _validate_sso_endpoint(url: str, label: str) -> None:
    """Validates an SSO endpoint before making the HTTP request."""
    if not url:
        raise ValueError(f"{label} not configured")
    if settings.is_production:
        scheme = (urlparse(url).scheme or "").lower()
        if scheme != "https":
            raise ValueError(f"{label} must use https in production")
    try:
        validate_outbound_url(url)  # blocks localhost/private IP
    except HTTPException as exc:
        raise ValueError(f"{label} invalid: {exc.detail}")
