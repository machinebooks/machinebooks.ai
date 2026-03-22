# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/workflows/dpia_workflow.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class DPIAWorkflowState:
    """Estado compartido entre los agentes del workflow DPIA."""
    treatment_id: str = ""
    treatment_data: dict = field(default_factory=dict)
    privacy_analysis: dict = field(default_factory=dict)
    risk_assessment: dict = field(default_factory=dict)
    compliance_check: dict = field(default_factory=dict)
    final_report: str = ""
    steps: List[OrchestratorStep] = field(default_factory=list)
    total_tokens: int = 0
    total_cost_eur: float = 0.0

class DPIAWorkflow:
    """
    Workflow DPIA: 4 agentes en secuencia.
    Cada agente recibe el estado acumulado y lo enriquece.
    """

    WORKFLOW_STEPS = [
        {
            "agent": "privacy",
            "action": "analyze_treatment",
            "description": "Analizar el tratamiento: base jurídica, categorías de datos, "
                          "interesados, finalidades, plazos de conservación",
        },
        {
            "agent": "risk",
            "action": "assess_dpia_risks",
            "description": "Evaluar riesgos para los derechos y libertades: "
                          "probabilidad e impacto según criterios AEPD",
        },
        {
            "agent": "compliance",
            "action": "verify_dpia_compliance",
            "description": "Verificar cumplimiento de criterios Art. 35 RGPD "
                          "y lista de la AEPD de tratamientos que requieren DPIA",
        },
        {
            "agent": "report_writer",
            "action": "generate_dpia_report",
            "description": "Generar el documento DPIA completo con estructura "
                          "estándar: descripción, necesidad, proporcionalidad, "
                          "riesgos, medidas, conclusión",
        },
    ]

    def __init__(self, agent_registry, rag_service):
        self.agent_registry = agent_registry
        self.rag_service = rag_service

    async def execute(
        self, treatment_id: str, tenant_id: str
    ) -> AsyncGenerator[dict, None]:
        """
        Ejecuta el workflow DPIA paso a paso,
        emitiendo eventos SSE en cada transición.
        """
        state = DPIAWorkflowState(treatment_id=treatment_id)

        for i, step_def in enumerate(self.WORKFLOW_STEPS):
            step = OrchestratorStep(
                agent_name=step_def["agent"],
                action=step_def["action"],
            )

            # Notificar inicio del paso
            yield {
                "type": "step_transition",
                "step_number": i + 1,
                "total_steps": len(self.WORKFLOW_STEPS),
                "agent": step_def["agent"],
                "description": step_def["description"],
                "status": "running",
            }

            # Obtener el agente del registro
            agent = self.agent_registry.get(step_def["agent"])

            try:
                # Ejecutar el agente con el estado acumulado
                result = await agent.execute(
                    action=step_def["action"],
                    context={
                        "treatment_id": treatment_id,
                        "tenant_id": tenant_id,
                        "accumulated_state": state.__dict__,
                    },
                )

                # Actualizar estado compartido con los resultados
                self._update_state(state, step_def["agent"], result)

                step.status = "completed"
                step.tokens_used = result.tokens_used
                step.cost_eur = result.cost_eur
                step.output_summary = result.summary

                state.total_tokens += result.tokens_used
                state.total_cost_eur += result.cost_eur

                # Notificar fin del paso con métricas
                yield {
                    "type": "agent_completed",
                    "agent": step_def["agent"],
                    "summary": result.summary,
                    "tokens": result.tokens_used,
                    "cost_eur": round(result.cost_eur, 4),
                }

            except Exception as e:
                step.status = "failed"
                yield {
                    "type": "error",
                    "agent": step_def["agent"],
                    "message": f"Error en {step_def['agent']}: {str(e)}",
                }
                # En caso de fallo, no abortamos todo el workflow:
                # registramos el error y continuamos con lo que hay
                # El CISO decide si el resultado parcial es suficiente

            state.steps.append(step)

        # Emitir resumen final
        yield {
            "type": "workflow_completed",
            "treatment_id": treatment_id,
            "total_steps": len(state.steps),
            "completed_steps": sum(1 for s in state.steps if s.status == "completed"),
            "total_tokens": state.total_tokens,
            "total_cost_eur": round(state.total_cost_eur, 4),
        }

    def _update_state(self, state: DPIAWorkflowState, agent_name: str, result):
        """Actualiza el estado compartido según el agente que acaba de ejecutar."""
        if agent_name == "privacy":
            state.privacy_analysis = result.data
        elif agent_name == "risk":
            state.risk_assessment = result.data
        elif agent_name == "compliance":
            state.compliance_check = result.data
        elif agent_name == "report_writer":
            state.final_report = result.data.get("report_text", "")
