# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
async def _direct_ping(cls, deployment, *, embedding: bool) -> None:
    """Calls the provider's SDK directly."""
    client = AsyncOpenAI(
        api_key=deployment.api_key,
        base_url=deployment.endpoint,
    )
    await client.chat.completions.create(
        model=deployment.deployment_name or deployment.model_key,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=64,  # configurable
    )
