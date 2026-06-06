# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# Ejemplo de verificación en el receptor del webhook
def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature.replace("sha256=", ""))
