# Extracted from: LibroAIGateway/cap-01-gateway-architecture-contract.md
class BaseLLMAdapter(ABC):
    provider_name: str = "unknown"

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse: ...

    @abstractmethod
    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[StreamChunk]: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    async def chat_with_retry(self, request, max_retries=3, base_delay=2.0):
        """Retry with exponential backoff for transient errors."""
