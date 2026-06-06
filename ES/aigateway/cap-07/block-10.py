# Extraído de: LibroAIGateway/cap-07-adapters.md
def _translate_tools(self, tools):
    result = []
    for t in tools:
        fn = t.get("function") or {}
        result.append({
            "name": fn.get("name"),
            "description": fn.get("description") or "",
            "input_schema": fn.get("parameters") or {"type": "object", "properties": {}},
        })
    return result
