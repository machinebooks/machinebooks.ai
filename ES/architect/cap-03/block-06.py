# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
# Ejemplo didáctico: agente con herramientas usando Claude Agent SDK
import anthropic

client = anthropic.Anthropic()

# Definir herramientas disponibles para el agente
tools = [
    {
        "name": "search_documents",
        "description": "Busca documentos relevantes en la base de conocimiento",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Consulta de búsqueda"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
]

# El agente razona, llama herramientas y compone la respuesta final
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "¿Cuáles son los requisitos técnicos de este proyecto?"
    }]
)

# Si el modelo decide llamar una herramienta, el SDK lo indica
if response.stop_reason == "tool_use":
    # Extraer la llamada a herramienta y ejecutarla
    tool_use = next(b for b in response.content if b.type == "tool_use")
    tool_result = execute_tool(tool_use.name, tool_use.input)
    # Continuar el ciclo con el resultado
