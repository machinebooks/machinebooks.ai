# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
import anthropic
from typing import Any

client = anthropic.Anthropic()

class AutonomousAgent:
    """
    Agente con bucle ReAct que itera hasta alcanzar el objetivo
    o superar el número máximo de iteraciones.
    """

    def __init__(self, agent_def: AgentDefinition, tool_registry: dict):
        self.agent_def = agent_def
        self.tools = self._build_tool_schemas(tool_registry)
        self.max_iterations = 10
        self.memory = []  # Memoria de trabajo de la sesión

    def run(self, user_message: str, session_context: dict) -> dict:
        """
        Ejecuta el bucle agentic hasta completar la tarea o agotar iteraciones.
        """
        messages = self._build_initial_messages(user_message, session_context)
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # Act: invocar Claude con las herramientas disponibles
            response = client.messages.create(
                model=self.agent_def.model_id,
                max_tokens=self.agent_def.max_tokens,
                system=self.agent_def.system_prompt,
                tools=self.tools,
                messages=messages
            )

            # Observe: ¿Claude ha terminado o necesita invocar herramientas?
            if response.stop_reason == "end_turn":
                # Reflect: tarea completada, extraer respuesta final
                final_text = self._extract_text(response)
                self._update_memory(user_message, final_text)
                return {
                    "status": "completed",
                    "response": final_text,
                    "iterations": iteration
                }

            if response.stop_reason == "tool_use":
                # Claude solicita ejecutar una o más herramientas
                tool_results = self._execute_tools(response)

                # Añadir respuesta de Claude y resultados al historial
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                # Loop: continuar el bucle con los resultados
                continue

        # Límite de iteraciones alcanzado
        return {
            "status": "max_iterations_reached",
            "response": "No fue posible completar la tarea en el número máximo de pasos.",
            "iterations": iteration
        }

    def _execute_tools(self, response) -> list:
        """Ejecuta todas las herramientas solicitadas por Claude y retorna los resultados."""
        results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_fn = self.tool_registry.get(block.name)
                if tool_fn:
                    try:
                        # Validar argumentos contra el esquema de la herramienta
                        # antes de ejecutar — previene tipos incorrectos o campos extra
                        result = tool_fn(**block.input)
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result)
                        })
                    except Exception as e:
                        results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Error al ejecutar herramienta: {str(e)}",
                            "is_error": True
                        })
        return results
