# Extraído de: LibroAIGateway/cap-09-compresion-tokens.md
# gateway/app/services/token_counter.py:126-181 (sintetizado)
async def count_anthropic_tokens_async(messages, model, system=None, tools=None):
    """Contador nativo Anthropic — más preciso pero requiere HTTP."""
    if not messages or not model:
        return None
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages/count_tokens",
            json={"model": model, "messages": messages, ...},
            headers={"x-api-key": api_key, ...},
        )
        if r.status_code == 200:
            return r.json().get("input_tokens")
    return None  # fallback a tiktoken con cl100k_base en el caller
