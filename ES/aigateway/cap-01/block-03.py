# Extraído de: LibroAIGateway/cap-01-gateway-arquitectura-contrato.md
# ChatCompletionRequest — schema de entrada (fragmento)
class ChatCompletionRequest(BaseModel):
    model: str | None = None              # modelo solicitado
    messages: list[Message]               # conversación
    temperature: float | None = None      # temperatura
    max_tokens: int | None = None         # cap de salida
    stream: bool = False                  # streaming?
    purpose: str | None = None            # purpose corporativo
    tools: list[dict] | None = None       # tool definitions
    tool_choice: str | dict | None = None
    parallel_tool_calls: bool | None = None
