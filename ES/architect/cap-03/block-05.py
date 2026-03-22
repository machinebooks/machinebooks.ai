# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Ejemplo didáctico de servidor MCP con herramienta de búsqueda
# El agente puede llamar search_documents con los parámetros validados
# El servidor gestiona la autenticación y el acceso al sistema externo

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "search_documents":
        # Validar parámetros antes de ejecutar
        query = arguments.get("query", "")
        max_results = min(arguments.get("max_results", 10), 50)  # límite máximo

        # Ejecutar con usuario de solo lectura y timeout
        results = await document_service.search(
            query=query,
            max_results=max_results,
            timeout_seconds=10
        )
        return [TextContent(type="text", text=format_results(results))]
