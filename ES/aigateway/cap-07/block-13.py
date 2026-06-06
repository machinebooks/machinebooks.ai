# Extraído de: LibroAIGateway/cap-07-adapters.md
def _to_responses_input(self, messages) -> list:
    out = []
    for m in messages:
        if m.role in ("user", "system", "developer"):
            out.append({"role": m.role,
                "content": [{"type": "input_text", "text": m.content or ""}]})
        if m.role == "assistant" and m.tool_calls:
            for tc in m.tool_calls:
                out.append({
                    "type": "function_call",
                    "call_id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": tc["function"]["arguments"],
                })
        if m.role == "tool":
            out.append({
                "type": "function_call_output",
                "call_id": m.tool_call_id or "",
                "output": m.content,
            })
    return out
