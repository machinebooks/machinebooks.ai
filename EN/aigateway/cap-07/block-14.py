# Extracted from: LibroAIGateway/cap-07-adapters.md
def _build_payload(self, request) -> dict:
    messages, system = [], []
    for m in request.messages:
        if m.role == "system":
            system.append({"text": m.content})
        elif m.role == "tool":
            pending.append({
                "toolResult": {
                    "toolUseId": m.tool_call_id,
                    "content": [{"text": m.content}],
                }
            })
        elif m.role == "assistant":
            blocks = []
            if m.content: blocks.append({"text": m.content})
            if m.tool_calls:
                for tc in m.tool_calls:
                    blocks.append({"toolUse": {
                        "toolUseId": tc["id"],
                        "name": tc["function"]["name"],
                        "input": json.loads(tc["function"]["arguments"]),
                    }})
            messages.append({"role": "assistant", "content": blocks})
    return {"modelId": request.model, "messages": messages,
            "inferenceConfig": {"temperature": request.temperature}}
