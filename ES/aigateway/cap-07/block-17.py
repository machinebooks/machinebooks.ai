# Extraído de: LibroAIGateway/cap-07-adapters.md
def _build_payload(self, request, stream):
    messages = self._build_openai_messages(request.messages)
    system_prompt = None
    history = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            history.append(msg)
    # Último user message → input; el resto → historial embebido
    last_input = history[-1]["content"] if history[-1]["role"] == "user" else ""
