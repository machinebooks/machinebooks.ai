# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# Example verification on the webhook receiver
def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature.replace("sha256=", ""))
