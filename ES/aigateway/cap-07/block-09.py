# Extraído de: LibroAIGateway/cap-07-adapters.md
def _translate_messages(self, messages, system_min_chars=4000):
    system_parts = []
    conversation = []
    pending_tool_results = []

    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
            continue
        if m.role == "tool":
            pending_tool_results.append({
                "type": "tool_result",
                "tool_use_id": m.tool_call_id or "",
                "content": m.content or "",
            })
            continue
        # assistant: text + tool_use blocks
        if m.role == "assistant":
            blocks = []
            if m.content:
                blocks.append({"type": "text", "text": m.content})
            if m.tool_calls:
                for tc in m.tool_calls:
                    blocks.append({"type": "tool_use", ...})
            if blocks:
                conversation.append({"role": "assistant", "content": blocks})
    return "\n\n".join(system_parts), conversation
