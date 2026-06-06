# Extracted from: LibroAIGateway/cap-01-gateway-architecture-contract.md
# What the adapter returns — normalized, provider-independent
@dataclass
class ChatResponse:
    content: str                    # generated text
    model: str                     # actual model that responded
    prompt_tokens: int             # input tokens
    completion_tokens: int         # output tokens
    finish_reason: str = "stop"
    tool_calls: list[dict] | None = None
    reasoning: str | None = None   # reasoning (thinking models)
    cached_tokens: int = 0         # subset served from cache
