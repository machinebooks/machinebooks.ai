# Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
# services/agent_budget_manager.py
# Gestiona el presupuesto de ejecución de agentes autónomos.
# Proporciona al agente visibilidad de su coste y permite decisiones adaptativas.

from datetime import datetime
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class WorkflowBudget:
    """
    Presupuesto asignado a una ejecución de workflow de agente.
    El agente recibe este objeto al inicio y lo consulta
    para adaptar su estrategia de ejecución.
    """
    workflow_id: str
    objetivo: str
    presupuesto_total_eur: Decimal
    presupuesto_restante_eur: Decimal
    tiempo_inicio: datetime
    tiempo_limite_segundos: int

    # Umbrales para decisiones adaptativas del agente
    umbral_simplificar_pct: float = 0.70   # Simplificar si queda < 70%
    umbral_escalar_pct: float = 0.20       # Escalar si queda < 20%
    umbral_detener_pct: float = 0.05       # Detener si queda < 5%

    # Trazabilidad de costes por sub-agente
    costes_por_agente: dict = field(default_factory=dict)

    # Historial de llamadas
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
        Registra un coste y actualiza el presupuesto restante.
        Returns True si dentro de presupuesto, False si insuficiente.
        """
        if coste_eur > self.presupuesto_restante_eur:
            return False

        self.presupuesto_restante_eur -= coste_eur
        self.coste_acumulado_eur += coste_eur
        self.num_llamadas_llm += 1

        # Registrar por sub-agente para trazabilidad
        if agente_id not in self.costes_por_agente:
            self.costes_por_agente[agente_id] = Decimal("0.00")
        self.costes_por_agente[agente_id] += coste_eur
        return True
