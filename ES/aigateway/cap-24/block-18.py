# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# event_webhook_service.py: guard SSRF (sintético)
def validate_outbound_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise WebhookValidationError("Solo URLs HTTPS permitidas")
    if _is_internal_ip(parsed.hostname):
        raise WebhookValidationError("URL apunta a dirección interna")
# El cliente se construye con follow_redirects=False (ver 3.5.2):
# un redirect no debe poder saltarse esta validación.
