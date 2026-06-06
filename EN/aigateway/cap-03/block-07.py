# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# filter: tool result wrapper (defense against prompt injection via tools)
def _wrap_tool_result(text: str, tool_name, tool_call_id) -> str:
    name = tool_name or "unknown"
    tid = tool_call_id or ""
    return (
        f"<<TOOL_RESULT name=\"{name}\" id=\"{tid}\">\n"
        f"{text}\n"
        f"<</TOOL_RESULT>>"
    )
