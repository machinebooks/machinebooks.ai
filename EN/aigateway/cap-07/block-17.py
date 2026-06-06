# Extracted from: LibroAIGateway/cap-07-adapters.md
def _build_payload(self, request, stream):
    messages = self._build_openai_messages(request.messages)
    system_prompt = None
    history = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            history.append(msg)
    # Last user message → input; the rest → embedded history
    last_input = history[-1]["content"] if history[-1]["role"] == "user" else ""
