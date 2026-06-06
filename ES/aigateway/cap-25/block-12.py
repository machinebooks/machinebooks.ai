# Extraído de: LibroAIGateway/cap-25-mcp-registro-catalogo.md
def _extract_params_schema(parameters: list, root_spec: dict) -> dict:
    """Construye JSON Schema object desde lista de parámetros OpenAPI."""
    props: dict[str, Any] = {}
    required: list[str] = []
    for param in parameters:
        name = param.get("name", "")
        entry = _openapi_schema_to_json_schema(param.get("schema"), root_spec)
        if param.get("description"):
            entry["description"] = param["description"]
        props[name] = entry
        if param.get("required"):
            required.append(name)
    result = {"type": "object", "properties": props}
    if required:
        result["required"] = required
    return result
