# Extracted from: LibroAIGateway/cap-07-adapters.md
async def chat(self, request: ChatRequest) -> ChatResponse:
    payload = {
        "model": request.model,
        "messages": self._build_openai_messages(request.messages),
        "stream": False,
        "options": {
            "temperature": request.temperature,
            "num_predict": request.max_tokens,
        },
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{self._base_url}/api/chat", json=payload)
    data = resp.json()
    return ChatResponse(
        content=data["message"]["content"],
        prompt_tokens=data.get("prompt_eval_count", 0),
        completion_tokens=data.get("eval_count", 0),
    )
