# Extraído de: LibroAIGateway/cap-01-gateway-arquitectura-contrato.md
# Lo que el adapter devuelve — normalizado, independiente del proveedor
@dataclass
class ChatResponse:
    content: str                    # texto generado
    model: str                     # modelo real que respondió
    prompt_tokens: int             # tokens de entrada
    completion_tokens: int         # tokens de salida
    finish_reason: str = "stop"
    tool_calls: list[dict] | None = None
    reasoning: str | None = None   # reasoning (modelos con thinking)
    cached_tokens: int = 0         # subset servido desde cache
