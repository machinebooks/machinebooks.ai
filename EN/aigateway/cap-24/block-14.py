# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# event_webhook_service.py (synthetic)
import hmac, hashlib

def _sign(payload: str, secret: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

async def deliver(self, config: WebhookConfig, event_key: str, payload: str, delivery_id: str):
    signature = _sign(payload, config.secret)
    headers = {
        "Content-Type": "application/json",
        "X-N7x-Event": event_key,
        "X-N7x-Delivery": delivery_id,
        "X-N7x-Signature": f"sha256={signature}",
        "User-Agent": "N7x-Webhook/1.0",
    }
    # follow_redirects=False: a 30x must not pull us off the validated host (anti-SSRF)
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        return await client.post(config.url, content=payload, headers=headers)
