# Source: The FinOps Engineer and the Machine -- Chapter 27
# Pattern: Fair use monitoring for SaaS plans

# services/fair_use_monitor.py
# Usage monitor that detects heavy users exceeding fair use
# and generates alerts before the customer gets a surprise.

from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.llm_usage_log import LLMUsageLog


@dataclass
class AlertaFairUse:
    """Alert for a customer approaching or exceeding fair use."""
    cliente_id: str
    plan: str
    num_usuarios: int

    # Current usage vs plan limits
    operaciones_mes: int
    limite_operaciones_mes: int
    pct_uso: float

    # Full month projection
    operaciones_proyectadas_mes: int
    superara_limite: bool

    # Economic impact
    coste_real_mes_eur: float
    ingreso_mes_eur: float
    margen_actual_pct: float

    # Recommendation
    accion_recomendada: str  # "notify", "propose_upgrade", "apply_overage"


class FairUseMonitor:
    """
    Monitors each customer's usage and generates alerts when they
    approach the fair use limits.

    Objectives:
    1. Detect heavy users before they impact margins
    2. Generate proactive (not reactive) upgrade conversations
    3. Calculate margin impact in real time
    """

    # Alert thresholds (% of fair use limit)
    UMBRAL_AVISO = 0.70      # Notify internal team at 70%
    UMBRAL_CLIENTE = 0.85    # Notify customer at 85%
    UMBRAL_OVERAGE = 1.00    # Start overage process at 100%

    def __init__(self, db: Session):
        self.db = db

    def analizar_cliente(
        self,
        cliente_id: str,
        plan: str,
        num_usuarios: int,
        precio_mensual_eur: float,
        limite_operaciones: int,
        dia_del_mes: Optional[int] = None,
    ) -> AlertaFairUse:
        """
        Analyzes a customer's usage and generates the corresponding alert.
        """
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)
        dia_actual = dia_del_mes or hoy.day
        dias_en_mes = 30  # Approximation

        # Customer operations month-to-date
        operaciones_mes = (
            self.db.query(func.count(LLMUsageLog.id))
            .filter(
                LLMUsageLog.cliente_id == cliente_id,
                LLMUsageLog.created_at >= primer_dia_mes,
            )
            .scalar() or 0
        )

        # Customer actual cost month-to-date
        coste_real = (
            self.db.query(func.sum(LLMUsageLog.cost_eur))
            .filter(
                LLMUsageLog.cliente_id == cliente_id,
                LLMUsageLog.created_at >= primer_dia_mes,
            )
            .scalar() or 0.0
        )

        # Project to full month
        factor_proyeccion = dias_en_mes / dia_actual
        operaciones_proyectadas = int(operaciones_mes * factor_proyeccion)
        coste_proyectado = float(coste_real) * factor_proyeccion

        pct_uso = operaciones_mes / limite_operaciones if limite_operaciones > 0 else 0

        # Calculate margin with projected real cost
        margen = (precio_mensual_eur - coste_proyectado) / precio_mensual_eur * 100

        # Determine recommended action
        if pct_uso >= self.UMBRAL_OVERAGE:
            accion = "aplicar_overage"
        elif pct_uso >= self.UMBRAL_CLIENTE:
            accion = "proponer_upgrade"
        elif pct_uso >= self.UMBRAL_AVISO:
            accion = "notificar_interno"
        else:
            accion = "ninguna"

        return AlertaFairUse(
            cliente_id=cliente_id,
            plan=plan,
            num_usuarios=num_usuarios,
            operaciones_mes=operaciones_mes,
            limite_operaciones_mes=limite_operaciones,
            pct_uso=round(pct_uso * 100, 1),
            operaciones_proyectadas_mes=operaciones_proyectadas,
            superara_limite=operaciones_proyectadas > limite_operaciones,
            coste_real_mes_eur=round(float(coste_real), 2),
            ingreso_mes_eur=precio_mensual_eur,
            margen_actual_pct=round(margen, 1),
            accion_recomendada=accion,
        )
