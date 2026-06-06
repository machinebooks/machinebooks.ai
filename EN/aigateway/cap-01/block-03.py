# Extracted from: LibroAIGateway/cap-01-gateway-architecture-contract.md
# ChatCompletionRequest — input schema (fragment)
class ChatCompletionRequest(BaseModel):
    model: str | None = None              # requested model
    messages: list[Message]               # conversation
    temperature: float | None = None      # temperature
    max_tokens: int | None = None         # output cap
    stream: bool = False                  # streaming?
    purpose: str | None = None            # corporate purpose
    tools: list[dict] | None = None       # tool definitions
    tool_choice: str | dict | None = None
    parallel_tool_calls: bool | None = None
