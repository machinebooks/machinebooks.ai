# Source: The FinOps Engineer and the Machine -- Chapter 28
# Pattern: Multi-agent orchestrator with cost tracking

# agents/orchestrator_with_billing.py
# Orchestrator that manages sub-agents with inter-agent billing.

from decimal import Decimal
from services.agent_budget_manager import AgentBudgetManager


class AgentOrchestrator:
    """
    Orchestrator that delegates tasks to sub-agents with budget control.

    Agent-to-agent billing pattern:
    1. The orchestrator receives a WorkflowBudget for the total budget
    2. When creating a sub-agent, it assigns a fraction of the budget
    3. The sub-agent's cost accumulates in the parent WorkflowBudget
    """

    def __init__(self, budget_manager: AgentBudgetManager):
        self.budget_manager = budget_manager

    def ejecutar_tarea_compleja(
        self, tarea: str,
        subtareas: list[dict],  # [{"nombre": "...", "pct_budget": 0.3}]
        presupuesto_total_eur: float,
    ) -> dict:
        """Decomposes task into subtasks with inter-agent billing."""
        budget_orquestador = self.budget_manager.crear_workflow_budget(
            objetivo=tarea,
            presupuesto_eur=presupuesto_total_eur,
        )

        resultados_subtareas = []

        for subtarea in subtareas:
            presupuesto_subtarea = (
                float(budget_orquestador.presupuesto_restante_eur)
                * subtarea.get("pct_budget", 0.25)
            )

            if presupuesto_subtarea < 0.01:
                resultados_subtareas.append({
                    "subtarea": subtarea["nombre"],
                    "estado": "omitida_por_presupuesto",
                })
                continue

            # Sub-agent with its budget fraction
            sub_agente = BudgetAwareAgent(self.budget_manager)
            resultado_sub = sub_agente.ejecutar_con_budget(
                objetivo=subtarea["objetivo"],
                presupuesto_eur=presupuesto_subtarea,
                tools=[], tool_executor=lambda n, i: {},
            )

            # Sub-agent cost propagates to the orchestrator's budget
            coste_sub = Decimal(
                str(resultado_sub["workflow"]["coste_total_eur"])
            )
            budget_orquestador.registrar_coste(
                coste_eur=coste_sub,
                agente_id=f"subagente_{subtarea['nombre']}",
                descripcion=f"Subtarea: {subtarea['objetivo'][:50]}",
            )

            resultados_subtareas.append({
                "subtarea": subtarea["nombre"],
                "estado": resultado_sub["resultado"]["estado"],
                "coste_eur": float(coste_sub),
            })

        resumen = self.budget_manager.get_resumen_costes(
            budget_orquestador.workflow_id
        )
        return {
            "orquestador": resumen,
            "subtareas": resultados_subtareas,
            "coste_total_eur": resumen["coste_total_eur"],
        }
