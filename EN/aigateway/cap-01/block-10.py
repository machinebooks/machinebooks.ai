# Extracted from: LibroAIGateway/cap-01-gateway-architecture-contract.md
# What the adapter receives — normalized, no noise
@dataclass
class ChatRequest:
    messages: list[ChatMessage]    # parsed messages
    model: str                    # model chosen by the router
    temperature: float            # effective temperature
    max_tokens: int | None        # token cap
    stream: bool = False          # streaming mode
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None
    request_id: str | None = None  # for e2e correlation
