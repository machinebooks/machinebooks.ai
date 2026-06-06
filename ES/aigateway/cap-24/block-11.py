# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# gateway/app/services/event_bus.py (sintético)
import asyncio

class EventBus:
    def __init__(self, redis_publisher, webhook_service):
        self._redis = redis_publisher
        self._webhooks = webhook_service

    def fire(self, event_key: str, *, organization_id: int | None, data: dict) -> None:
        # No incrementa métricas. Solo lanza dos tareas independientes.
        envelope = {"event": event_key, "organization_id": organization_id, "data": data}
        asyncio.create_task(self._redis.publish("gateway_events", envelope))   # WebSocket
        asyncio.create_task(self._webhooks.dispatch(event_key, organization_id, data))  # webhooks
