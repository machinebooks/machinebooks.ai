# Extraído de: LibroAIGateway/cap-07-adapters.md
async def chat(self, request: ChatRequest) -> ChatResponse:
    create_kwargs = {
        "model": request.model,
        "messages": self._build_openai_messages(request.messages),
        "stream": False,
        **_filter_extra(request.extra_params),
    }
    response = await self._client.chat.completions.create(**create_kwargs)
    choice = response.choices[0]
    return ChatResponse(
        content=choice.message.content or "",
        model=response.model,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        cached_tokens=cached_tokens,
        tool_calls=tool_calls,
    )
