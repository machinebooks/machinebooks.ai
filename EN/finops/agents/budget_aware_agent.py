# Source: The FinOps Engineer and the Machine -- Chapter 28
# Pattern: Budget-aware Claude agent

# agents/budget_aware_agent.py
# Agent that incorporates its budget as active context in each call.
# Adapts its execution strategy based on remaining budget.

import anthropic
import json
from decimal import Decimal
from services.agent_budget_manager import AgentBudgetManager, WorkflowBudget


class BudgetAwareAgent:
    """
    Autonomous agent with integrated budget awareness.
    1. Budget context is injected into each model call
    2. The agent can decide to simplify or stop based on budget
    3. The cost of each call is recorded in the WorkflowBudget
    4. Sub-agents use the same budget (agent-to-agent billing)
    """

    def __init__(self, budget_manager: AgentBudgetManager):
        self.client = anthropic.Anthropic()
        self.budget_manager = budget_manager

    def ejecutar_con_budget(
        self, objetivo: str, presupuesto_eur: float,
        tools: list[dict], tool_executor: callable,
        modelo: str = "claude-sonnet-4-6",
    ) -> dict:
        """Execute an agent workflow with controlled budget."""
        budget = self.budget_manager.crear_workflow_budget(
            objetivo=objetivo,
            presupuesto_eur=presupuesto_eur,
            tiempo_limite_segundos=300,
        )

        system_prompt = f"""You are an agent that completes tasks efficiently.

Your objective: {objetivo}

{budget.generar_contexto_para_agente()}

EFFICIENCY INSTRUCTIONS:
- If budget is TIGHT: use fewer tools, be more direct.
- If budget is LOW: simplify as much as possible, deliver the essentials.
- If budget is CRITICAL: stop execution and deliver partial result.
- Explain in your final response what you completed and what remains pending."""

        messages = [{"role": "user", "content": objetivo}]
        resultado_final = None
        iteracion = 0
        max_iteraciones = 20  # Safety limit

        while iteracion < max_iteraciones:
            iteracion += 1

            # Check limits before each call
            if budget.debe_detenerse or budget.tiempo_agotado:
                resultado_final = {
                    "estado": "detenido_por_presupuesto",
                    "razon": "presupuesto_critico" if budget.debe_detenerse
                             else "tiempo_agotado",
                    "coste_eur": float(budget.coste_acumulado_eur),
                }
                break

            response = self.client.messages.create(
                model=modelo, max_tokens=2048,
                system=system_prompt, tools=tools,
                messages=messages,
            )

            # Record cost of this call
            coste_llamada = self._calcular_coste_llamada(
                modelo, response.usage.input_tokens,
                response.usage.output_tokens
            )
            budget.registrar_coste(
                coste_eur=coste_llamada, agente_id="principal",
                descripcion=f"Iteration {iteracion}",
            )

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        resultado = tool_executor(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(resultado, default=str),
                        })
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                texto = next(
                    (b.text for b in response.content if hasattr(b, "text")), ""
                )
                resultado_final = {
                    "estado": "completado", "resultado": texto,
                    "coste_eur": float(budget.coste_acumulado_eur),
                    "iteraciones": iteracion,
                }
                break

        resumen = self.budget_manager.get_resumen_costes(budget.workflow_id)
        return {"workflow": resumen, "resultado": resultado_final}
