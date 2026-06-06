# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# event_webhook_service.py: SSRF guard (synthetic)
def validate_outbound_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise WebhookValidationError("Only HTTPS URLs allowed")
    if _is_internal_ip(parsed.hostname):
        raise WebhookValidationError("URL points to an internal address")
# The client is built with follow_redirects=False (see 3.5.2):
# a redirect must not be able to bypass this validation.
