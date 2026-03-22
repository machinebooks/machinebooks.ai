# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
import anthropic
from typing import Any

class SecureAgentRunner:
    """Ejecutor de agente con controles de seguridad integrados."""

    def __init__(
        self,
        permissions: AgentPermissions,
        tools: list[SecureTool],
        system_prompt: str,
    ):
        self.permissions = permissions
        self.budget = AgentBudgetGuard(permissions)
        self.tools = self._filter_tools(tools)
        self.system_prompt = system_prompt
        self.client = anthropic.Anthropic()
        self.audit_log: list[dict] = []

    def _filter_tools(self, tools: list[SecureTool]) -> list[SecureTool]:
        """Solo admite herramientas del nivel de riesgo permitido."""
        allowed = []
        for tool in tools:
            if tool.risk_level in self.permissions.allowed_risk_levels:
                allowed.append(tool)
            else:
                self.audit_log.append({
                    "event": "tool_rejected",
                    "tool": tool.name,
                    "risk_level": tool.risk_level.value,
                    "reason": "Nivel de riesgo no permitido",
                })
        return allowed

    def _execute_tool(self, tool: SecureTool, args: dict) -> Any:
        """Ejecuta herramienta con verificación de presupuesto."""
        # 1. Verificar presupuesto antes de ejecutar
        self.budget.check_budget()

        # 2. Verificar si requiere aprobación humana
        if tool.requires_approval:
            approval = self._request_human_approval(tool, args)
            if not approval.approved:
                return {"status": "rejected", "reason": approval.reason}

        # 3. Verificar límite individual de la herramienta
        tool_calls = sum(
            1 for a in self.budget.state.actions_log
            if a["tool"] == tool.name
        )
        if tool_calls >= tool.max_calls_per_run:
            return {
                "status": "limit_reached",
                "message": f"{tool.name}: máximo {tool.max_calls_per_run} "
                           f"invocaciones por ejecución",
            }

        # 4. Ejecutar la herramienta
        result = tool.func(**args)

        # 5. Registrar la invocación
        self.budget.record_call(tool.name, tokens=0, args=args)

        return result

    def _request_human_approval(
        self, tool: SecureTool, args: dict,
    ) -> "ApprovalResponse":
        """Envía solicitud de aprobación y espera respuesta."""
        # Implementación conecta con Slack/webhook/email
        # según self.permissions.human_approval_channel
        ...

    def run(self, task: str) -> dict:
        """Ejecuta el agente con todas las capas de seguridad."""
        try:
            # Construir la lista de herramientas para Claude
            tool_definitions = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": _get_schema(t.func),
                }
                for t in self.tools
            ]

            # Invocar Claude con las herramientas filtradas
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=self.system_prompt,
                tools=tool_definitions,
                messages=[{"role": "user", "content": task}],
            )

            # Procesar tool_use en el response (bucle de agente)
            return self._agent_loop(response)

        except BudgetExceeded as e:
            self.audit_log.append({
                "event": "budget_exceeded",
                "dimension": e.dimension,
                "limit": e.limit,
                "actual": e.actual,
            })
            return {
                "status": "budget_exceeded",
                "partial_results": self.budget.state.actions_log,
                "error": str(e),
            }
