# Source: The FinOps Engineer and the Machine -- Chapter 24
# Pattern: FinOps Champion program service

# services/finops_champion.py
# Monthly FinOps Champion selection and notification.
# The process is transparent: criteria are public.

from datetime import date
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.llm_usage_log import LLMUsageLog
from models.task_completion_log import TaskCompletionLog
from services.cost_awareness_notifier import CostAwarenessNotifier


@dataclass
class CandidatoChampion:
    squad_codigo: str
    coste_eur_mes_actual: float
    coste_eur_mes_anterior: float
    eficiencia_actual: float   # ROI: value/cost
    eficiencia_anterior: float
    mejora_eficiencia_pct: float
    ahorro_absoluto_eur: float
    logro_principal: str       # Human-readable description of the achievement


class FinOpsChampionSelector:
    """
    Selects the monthly FinOps Champion based on efficiency improvement,
    not on lowest absolute cost.
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifier = CostAwarenessNotifier()

    def calcular_eficiencia_squad(
        self, squad: str, mes: date
    ) -> tuple[float, float]:
        """Returns (coste_eur, valor_generado_eur) for a squad in a month."""
        primer_dia = mes.replace(day=1)

        coste = self.db.query(
            func.sum(LLMUsageLog.cost_eur)
        ).filter(
            LLMUsageLog.squad_codigo == squad,
            func.date_trunc("month", LLMUsageLog.created_at) == primer_dia,
        ).scalar() or 0.0

        valor = self.db.query(
            func.sum(TaskCompletionLog.valor_generado_eur)
        ).filter(
            TaskCompletionLog.squad_codigo == squad,
            func.date_trunc("month", TaskCompletionLog.created_at) == primer_dia,
        ).scalar() or 0.0

        return float(coste), float(valor)

    def seleccionar_champion(self, mes_actual: date) -> Optional[CandidatoChampion]:
        """
        Selects the squad with the greatest efficiency improvement versus the previous month.
        Requires the squad to have had activity in both months.
        """
        # Calculate previous month
        if mes_actual.month == 1:
            mes_anterior = mes_actual.replace(year=mes_actual.year - 1, month=12)
        else:
            mes_anterior = mes_actual.replace(month=mes_actual.month - 1)

        # Get all active squads in the current month
        squads_activos = (
            self.db.query(LLMUsageLog.squad_codigo)
            .filter(
                func.date_trunc("month", LLMUsageLog.created_at) ==
                mes_actual.replace(day=1)
            )
            .distinct()
            .all()
        )

        mejor_candidato = None
        mejor_mejora = -float("inf")

        for (squad,) in squads_activos:
            coste_actual, valor_actual = self.calcular_eficiencia_squad(
                squad, mes_actual
            )
            coste_anterior, valor_anterior = self.calcular_eficiencia_squad(
                squad, mes_anterior
            )

            # Only compare squads with activity in both months
            if coste_anterior == 0 or valor_anterior == 0:
                continue

            eficiencia_actual = valor_actual / coste_actual if coste_actual > 0 else 0
            eficiencia_anterior = valor_anterior / coste_anterior

            mejora_pct = (
                (eficiencia_actual - eficiencia_anterior) / eficiencia_anterior * 100
            )
            ahorro_eur = coste_anterior - coste_actual

            if mejora_pct > mejor_mejora:
                mejor_mejora = mejora_pct
                mejor_candidato = CandidatoChampion(
                    squad_codigo=squad,
                    coste_eur_mes_actual=coste_actual,
                    coste_eur_mes_anterior=coste_anterior,
                    eficiencia_actual=eficiencia_actual,
                    eficiencia_anterior=eficiencia_anterior,
                    mejora_eficiencia_pct=mejora_pct,
                    ahorro_absoluto_eur=ahorro_eur,
                    logro_principal=(
                        f"Improved efficiency by {mejora_pct:.0f}% "
                        f"(from {eficiencia_anterior:.1f}x to {eficiencia_actual:.1f}x ROI)"
                    ),
                )

        return mejor_candidato
