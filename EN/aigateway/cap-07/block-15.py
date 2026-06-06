# Extracted from: LibroAIGateway/cap-07-adapters.md
_GENAI_LOCK = asyncio.Lock()

async def chat(self, request: ChatRequest) -> ChatResponse:
    async with _GENAI_LOCK:
        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(
            request.model, system_instruction=system,
            tools=tools if tools else None,
        )
        response = await model.generate_content_async(messages, ...)
    return ChatResponse(...)
