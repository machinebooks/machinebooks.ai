# Extraído de: LibroAIGateway/cap-07-adapters.md
@dataclass
class ChatMessage:
    role: str                     # system | user | assistant | tool
    content: str | list | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    reasoning_content: str | None = None

@dataclass
class ChatRequest:
    messages: list[ChatMessage]
    model: str
    temperature: float
    max_tokens: int | None
    stream: bool = False
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None
    parallel_tool_calls: bool | None = None
    extra_params: dict | None = None
    request_id: str | None = None

@dataclass
class ChatResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str = "stop"
    tool_calls: list[dict] | None = None
    reasoning: str | None = None
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    # ... campos adicionales (cache_read_input, preamble, etc.)
