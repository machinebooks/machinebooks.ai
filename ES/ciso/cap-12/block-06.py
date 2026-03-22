# Extraído de: LibroCISO/cap-12-agentes-especializados.md
from typing import Callable, Any
from dataclasses import dataclass, field


@dataclass
class ToolDefinition:
    """Definición formal de una herramienta para agentes."""
    name: str
    description: str
    handler: Callable[..., Any]
    parameters: dict            # JSON Schema de parámetros
    allowed_agents: list[str]   # Agentes que pueden usarla
    requires_auth: bool = True  # Si necesita contexto de usuario
    audit_level: str = "full"   # full | summary | none


class ToolRegistry:
    """Catálogo centralizado de herramientas para agentes.

    Controla qué herramienta puede usar cada agente,
    valida parámetros antes de ejecución y registra
    cada invocación para auditoría.
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Registra una herramienta en el catálogo."""
        self._tools[tool.name] = tool

    def invoke(self, tool_name: str, agent_name: str,
               params: dict, user_context: dict) -> Any:
        """Invoca una herramienta con validación y auditoría."""
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Herramienta '{tool_name}' no registrada")

        # Verificar que el agente tiene permiso
        if agent_name not in tool.allowed_agents:
            raise PermissionError(
                f"Agente '{agent_name}' no autorizado "
                f"para herramienta '{tool_name}'"
            )

        # Validar parámetros contra el schema
        self._validate_params(params, tool.parameters)

        # Ejecutar y registrar
        result = tool.handler(**params, user_context=user_context)

        return result

    def get_tools_for_agent(self, agent_name: str) -> list[dict]:
        """Devuelve las herramientas disponibles para un agente.

        Formato nativo de Claude Agent SDK tool definitions.
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.parameters
            }
            for t in self._tools.values()
            if agent_name in t.allowed_agents
        ]
