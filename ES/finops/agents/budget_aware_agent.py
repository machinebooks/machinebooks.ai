# Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
# agents/budget_aware_agent.py
# Agente que incorpora su presupuesto como contexto activo en cada llamada.
# Adapta su estrategia de ejecución según el presupuesto restante.

import anthropic
import json
from decimal import Decimal
from services.agent_budget_manager import AgentBudgetManager, WorkflowBudget


class BudgetAwareAgent:
    """
    Agente autónomo con conciencia de presupuesto integrada.
    1. El contexto de presupuesto se inyecta en cada llamada al modelo
    2. El agente puede decidir simplificar o detener según el presupuesto
    3. El coste de cada llamada se registra en el WorkflowBudget
    4. Los sub-agentes usan el mismo budget (agent-to-agent billing)
    """

    def __init__(self, budget_manager: AgentBudgetManager):
        self.client = anthropic.Anthropic()
        self.budget_manager = budget_manager

    def ejecutar_con_budget(
        self, objetivo: str, presupuesto_eur: float,
        tools: list[dict], tool_executor: callable,
        modelo: str = "claude-sonnet-4-6",
    ) -> dict:
        """Ejecuta un workflow de agente con presupuesto controlado."""
        budget = self.budget_manager.crear_workflow_budget(
            objetivo=objetivo,
            presupuesto_eur=presupuesto_eur,
            tiempo_limite_segundos=300,
        )

        system_prompt = f"""Eres un agente que completa tareas de forma eficiente.

Tu objetivo: {objetivo}

{budget.generar_contexto_para_agente()}

INSTRUCCIONES DE EFICIENCIA:
- Si el presupuesto está AJUSTADO: usa menos herramientas, sé más directo.
- Si el presupuesto está BAJO: simplifica al máximo, entrega lo esencial.
- Si el presupuesto es CRÍTICO: detén la ejecución y entrega resultado parcial.
- Explica en tu respuesta final qué completaste y qué quedó pendiente."""

        messages = [{"role": "user", "content": objetivo}]
        resultado_final = None
        iteracion = 0
        max_iteraciones = 20  # Límite de seguridad

        while iteracion < max_iteraciones:
            iteracion += 1

            # Verificar límites antes de cada llamada
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

            # Registrar coste de esta llamada
            coste_llamada = self._calcular_coste_llamada(
                modelo, response.usage.input_tokens,
                response.usage.output_tokens
            )
            budget.registrar_coste(
                coste_eur=coste_llamada, agente_id="principal",
                descripcion=f"Iteración {iteracion}",
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
