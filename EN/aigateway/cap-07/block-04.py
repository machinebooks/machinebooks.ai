# Extracted from: LibroAIGateway/cap-07-adapters.md
@dataclass
class StreamChunk:
    delta: str                              # incremental text
    finish_reason: str | None = None        # on the final chunk
    tool_calls_delta: list[dict] | None = None
    reasoning: str | None = None
    prompt_tokens: int | None = None        # only on final chunk (usage)
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    prompt_cache_key: str | None = None
