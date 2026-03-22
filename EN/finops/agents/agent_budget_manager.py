# Source: The FinOps Engineer and the Machine -- Chapter 28
# Pattern: Budget manager for autonomous agents

# services/agent_budget_manager.py
# Manages execution budget for autonomous agents.
# Provides the agent with cost visibility and enables adaptive decisions.

from datetime import datetime
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class WorkflowBudget:
    """
    Budget allocated to an agent workflow execution.
    The agent receives this object at startup and queries it
    to adapt its execution strategy.
    """
    workflow_id: str
    objetivo: str
    presupuesto_total_eur: Decimal
    presupuesto_restante_eur: Decimal
    tiempo_inicio: datetime
    tiempo_limite_segundos: int

    # Thresholds for adaptive agent decisions
    umbral_simplificar_pct: float = 0.70   # Simplify if < 70% remaining
    umbral_escalar_pct: float = 0.20       # Escalate if < 20% remaining
    umbral_detener_pct: float = 0.05       # Stop if < 5% remaining

    # Cost traceability per sub-agent
    costes_por_agente: dict = field(default_factory=dict)

    # Call history
    num_llamadas_llm: int = 0
    coste_acumulado_eur: Decimal = Decimal("0.00")

    @property
    def pct_presupuesto_restante(self) -> float:
        if self.presupuesto_total_eur == 0:
            return 0.0
        return float(self.presupuesto_restante_eur / self.presupuesto_total_eur)

    @property
    def debe_simplificar(self) -> bool:
        return self.pct_presupuesto_restante < self.umbral_simplificar_pct

    @property
    def debe_escalar(self) -> bool:
        return self.pct_presupuesto_restante < self.umbral_escalar_pct

    @property
    def debe_detenerse(self) -> bool:
        return self.pct_presupuesto_restante < self.umbral_detener_pct

    def registrar_coste(
        self, coste_eur: Decimal, agente_id: str, descripcion: str,
    ) -> bool:
        """
        Record a cost and update the remaining budget.
        Returns True if within budget, False if insufficient.
        """
        if coste_eur > self.presupuesto_restante_eur:
            return False

        self.presupuesto_restante_eur -= coste_eur
        self.coste_acumulado_eur += coste_eur
        self.num_llamadas_llm += 1

        # Record per sub-agent for traceability
        if agente_id not in self.costes_por_agente:
            self.costes_por_agente[agente_id] = Decimal("0.00")
        self.costes_por_agente[agente_id] += coste_eur
        return True

    def generar_contexto_para_agente(self) -> str:
        """
        Generate the budget context injected into the prompt.
        The agent reads this context to make adaptive decisions.
        """
        estado = "normal"
        instruccion = ""

        if self.debe_detenerse:
            estado = "CRITICAL"
            instruccion = (
                "STOP and deliver partial result with explanation."
            )
        elif self.debe_escalar:
            estado = "LOW"
            instruccion = (
                "Simplify as much as possible. Deliver only the essential result."
            )
        elif self.debe_simplificar:
            estado = "TIGHT"
            instruccion = (
                "Optimize efficiency. Avoid unnecessary calls."
            )

        return f"""[WORKFLOW FINANCIAL CONTEXT]
Total budget: €{self.presupuesto_total_eur:.4f}
Remaining budget: €{self.presupuesto_restante_eur:.4f} ({self.pct_presupuesto_restante*100:.1f}%)
Status: {estado}
LLM calls made: {self.num_llamadas_llm}
Time elapsed: {self.tiempo_transcurrido_segundos:.0f}s / {self.tiempo_limite_segundos}s
{"INSTRUCTION: " + instruccion if instruccion else ""}"""
