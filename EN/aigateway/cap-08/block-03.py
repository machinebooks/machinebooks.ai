# Extracted from: LibroAIGateway/cap-08-caching.md
# gateway/app/services/cache_service.py:272-323 (synthesized)
async def cached_response_as_sse_chunks(cached: dict, chunk_size_chars: int = 64):
    content = cached["choices"][0]["message"]["content"]
    response_id = cached.get("id") or f"cache-{int(time.time() * 1000)}"

    # Emit deltas of N characters with micro-delay for typewriter effect
    for i in range(0, len(content), chunk_size_chars):
        piece = content[i : i + chunk_size_chars]
        chunk = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}],
            "_n7x_cache_hit": True,
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.005)  # ~5ms between chunks

    # Final chunk with finish_reason + usage
    yield f"data: ...finish_reason: stop...\n\n"
    yield "data: [DONE]\n\n"
