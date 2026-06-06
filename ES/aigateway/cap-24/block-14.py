# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# event_webhook_service.py (sintético)
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
    # follow_redirects=False: un 30x no debe sacarnos del host validado (anti-SSRF)
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        return await client.post(config.url, content=payload, headers=headers)
