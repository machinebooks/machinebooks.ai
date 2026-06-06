# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# event_bus.py: publicación a Redis tolerante a fallos
async def _publish_to_redis(self, channel: str, envelope: dict):
    try:
        await self._redis.publish(channel, json.dumps(envelope))
    except RedisConnectionError:
        # Log pero no propaga: el evento de realtime se descarta, no se reintenta.
        logger.warning("Redis unavailable, realtime event skipped", event=envelope["event"])
