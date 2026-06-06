# Extraído de: LibroAIGateway/cap-01-gateway-arquitectura-contrato.md
# Lo que el adapter recibe — normalizado, sin ruido
@dataclass
class ChatRequest:
    messages: list[ChatMessage]    # mensajes parseados
    model: str                    # modelo elegido por el router
    temperature: float            # temperatura efectiva
    max_tokens: int | None        # cap de tokens
    stream: bool = False          # modo streaming
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None
    request_id: str | None = None  # para correlación e2e
