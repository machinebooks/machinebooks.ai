# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
import anthropic

# Cliente con soporte MCP integrado
client = anthropic.Anthropic()

def run_agent_with_mcp(
    user_message: str,
    internal_tools: list[dict],
    mcp_servers: list[dict]
) -> str:
    """
    Ejecuta el agente combinando herramientas internas con herramientas MCP.
    Las herramientas MCP se descubren automáticamente desde los servidores configurados.
    """
    # Las herramientas MCP se mezclan con las herramientas internas
    # Claude las usa con la misma sintaxis tool_use
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="Eres el asistente de la Plataforma. Usa las herramientas disponibles.",
        messages=[{"role": "user", "content": user_message}],
        tools=internal_tools,
        # Configuración de servidores MCP (acceso a sistemas externos)
        # Configuración detallada de servidores MCP: véase Capítulo 3
        # mcp_servers se configura en el cliente según la documentación del SDK
    )
    return response
