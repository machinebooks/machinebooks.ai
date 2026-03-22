# Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
# agents/orchestrator_with_billing.py
# Orquestador que gestiona sub-agentes con billing entre agentes.

from decimal import Decimal
from services.agent_budget_manager import AgentBudgetManager


class AgentOrchestrator:
    """
    Orquestador que delega tareas a sub-agentes con control de presupuesto.

    Patrón de agent-to-agent billing:
    1. El orquestador recibe un WorkflowBudget del presupuesto total
    2. Al crear un sub-agente, le asigna una fracción del presupuesto
    3. El coste del sub-agente se acumula en el WorkflowBudget padre
    """

    def __init__(self, budget_manager: AgentBudgetManager):
        self.budget_manager = budget_manager

    def ejecutar_tarea_compleja(
        self, tarea: str,
        subtareas: list[dict],  # [{"nombre": "...", "pct_budget": 0.3}]
        presupuesto_total_eur: float,
    ) -> dict:
        """Descompone tarea en subtareas con billing entre agentes."""
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

            # Sub-agente con su fracción del presupuesto
            sub_agente = BudgetAwareAgent(self.budget_manager)
            resultado_sub = sub_agente.ejecutar_con_budget(
                objetivo=subtarea["objetivo"],
                presupuesto_eur=presupuesto_subtarea,
                tools=[], tool_executor=lambda n, i: {},
            )

            # Coste del sub-agente sube al budget del orquestador
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
