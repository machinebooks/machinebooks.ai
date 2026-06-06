# Extracted from: LibroAIGateway/cap-07-adapters.md
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
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return await self.chat(request)
            except Exception as e:
                last_error = e
                is_retryable = any(k in str(e).lower() for k in (
                    "500","502","503","429","rate","timeout",
                    "overloaded","server_error","capacity",
                    "retry","temporarily"))
                if not is_retryable or attempt >= max_retries:
                    raise
                await asyncio.sleep(base_delay * (2 ** attempt))
