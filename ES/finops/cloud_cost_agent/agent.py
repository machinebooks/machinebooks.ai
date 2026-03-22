# Extraído de: LibroFinOps/cap-12-agente-coste-cloud.md
# cloud_cost_agent/agent.py
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SYSTEM_PROMPT = """Eres un experto en FinOps cloud con acceso a datos de facturación
de AWS y Azure en tiempo real. Tu función es:

1. Analizar costes cloud respondiendo preguntas en lenguaje natural
2. Detectar anomalías y variaciones significativas (>10% mes a mes)
3. Proporcionar contexto de negocio, no solo números
4. Recomendar acciones concretas con estimación de ahorro

Cuando respondas:
- Cita siempre los números exactos de las APIs (no redondees sin indicarlo)
- Indica si una variación es estadísticamente significativa o ruido normal
- Separa los hechos (datos de API) de tu interpretación
- Si no tienes datos suficientes para una conclusión, dilo explícitamente

Los datos de coste que ves son reales y se usarán para decisiones de gasto."""


async def run_cost_agent(user_question: str) -> str:
    """Ejecuta el agente de coste cloud para una pregunta en lenguaje natural."""

    # Conectamos con el servidor MCP de billing
    server_params = StdioServerParameters(
        command="python",
        args=["cloud_billing_mcp/server.py"],
        env=None  # Hereda las variables de entorno con credenciales cloud
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # El SDK descubre automáticamente las herramientas disponibles
            await session.initialize()

            client = anthropic.Anthropic()

            # Obtenemos las herramientas del servidor MCP
            tools = await session.list_tools()
            mcp_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                for tool in tools.tools
            ]

            messages = [{"role": "user", "content": user_question}]

            # Ciclo agentic: el modelo decide qué herramientas usar
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=mcp_tools,
                    messages=messages
                )

                # Si el modelo terminó de razonar, devolvemos la respuesta
                if response.stop_reason == "end_turn":
                    text_blocks = [
                        block.text for block in response.content
                        if hasattr(block, 'text')
                    ]
                    return "\n".join(text_blocks)

                # Si el modelo quiere usar una herramienta, la ejecutamos
                if response.stop_reason == "tool_use":
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            # Llamamos al servidor MCP con los parámetros del modelo
                            result = await session.call_tool(
                                block.name,
                                arguments=block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                                if result.content else ""
                            })

                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
