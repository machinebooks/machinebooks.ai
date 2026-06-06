# Extraído de: LibroAIGateway/cap-07-adapters.md
ChatResponse(
    content="",
    tool_calls=[{
        "id": "toolu_abc123",
        "type": "function",
        "function": {
            "name": "search_cve",
            "arguments": '{"cve_id": "CVE-2025-1234"}',
        },
    }],
    finish_reason="tool_calls",  # mapeado desde "tool_use"
)
