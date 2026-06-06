# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# event_bus.py: fault-tolerant Redis publication
async def _publish_to_redis(self, channel: str, envelope: dict):
    try:
        await self._redis.publish(channel, json.dumps(envelope))
    except RedisConnectionError:
        # Log but does not propagate: the realtime event is dropped, not retried.
        logger.warning("Redis unavailable, realtime event skipped", event=envelope["event"])
