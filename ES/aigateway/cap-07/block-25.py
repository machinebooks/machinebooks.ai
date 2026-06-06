# Extraído de: LibroAIGateway/cap-07-adapters.md
async def stream_chat(self, request) -> AsyncIterator[StreamChunk]:
    stream = await self._client.messages.stream(...)
    async with stream as response:
        async for event in response:
            if event.type == "content_block_delta":
                yield StreamChunk(delta=event.delta.text)
            elif event.type == "message_delta":
                yield StreamChunk(
                    delta="", finish_reason=STOP_MAP.get(event.delta.stop_reason),
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    cached_tokens=read_tokens,
                )
