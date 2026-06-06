# Extraído de: LibroAIGateway/cap-07-adapters.md
@dataclass
class StreamChunk:
    delta: str                              # texto incremental
    finish_reason: str | None = None        # en el chunk final
    tool_calls_delta: list[dict] | None = None
    reasoning: str | None = None
    prompt_tokens: int | None = None        # solo en chunk final (usage)
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    prompt_cache_key: str | None = None
