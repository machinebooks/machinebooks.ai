# Extraído de: LibroFinOps/cap-27-caso-pricing-saas.md
# services/fair_use_monitor.py
# Monitor de uso que detecta heavy users que superan el fair use
# y genera alertas antes de que el cliente reciba una sorpresa.

from datetime import date, timedelta
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.llm_usage_log import LLMUsageLog


@dataclass
class AlertaFairUse:
    """Alerta de cliente que se aproxima o supera el fair use."""
    cliente_id: str
    plan: str
    num_usuarios: int

    # Uso actual vs límites del plan
    operaciones_mes: int
    limite_operaciones_mes: int
    pct_uso: float

    # Proyección del mes completo
    operaciones_proyectadas_mes: int
    superara_limite: bool

    # Impacto económico
    coste_real_mes_eur: float
    ingreso_mes_eur: float
    margen_actual_pct: float

    # Recomendación
    accion_recomendada: str  # "notificar", "proponer_upgrade", "aplicar_overage"


class FairUseMonitor:
    """
    Monitoriza el uso de cada cliente y genera alertas cuando
    se aproximan a los límites de fair use.

    Objetivos:
    1. Detectar heavy users antes de que impacten en márgenes
    2. Generar conversaciones de upgrade proactivas (no reactivas)
    3. Calcular el impacto de márgenes en tiempo real
    """

    # Umbrales de alerta (% del límite de fair use)
    UMBRAL_AVISO = 0.70      # Avisar al equipo interno al 70%
    UMBRAL_CLIENTE = 0.85    # Notificar al cliente al 85%
    UMBRAL_OVERAGE = 1.00    # Iniciar proceso de overage al 100%

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
        Analiza el uso de un cliente y genera la alerta correspondiente.
        """
        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)
        dia_actual = dia_del_mes or hoy.day
        dias_en_mes = 30  # Aproximación

        # Operaciones del cliente en lo que va de mes
        operaciones_mes = (
            self.db.query(func.count(LLMUsageLog.id))
            .filter(
                LLMUsageLog.cliente_id == cliente_id,
                LLMUsageLog.created_at >= primer_dia_mes,
            )
            .scalar() or 0
        )

        # Coste real del cliente en lo que va de mes
        coste_real = (
            self.db.query(func.sum(LLMUsageLog.cost_eur))
            .filter(
                LLMUsageLog.cliente_id == cliente_id,
                LLMUsageLog.created_at >= primer_dia_mes,
            )
            .scalar() or 0.0
        )

        # Proyectar al mes completo
        factor_proyeccion = dias_en_mes / dia_actual
        operaciones_proyectadas = int(operaciones_mes * factor_proyeccion)
        coste_proyectado = float(coste_real) * factor_proyeccion

        pct_uso = operaciones_mes / limite_operaciones if limite_operaciones > 0 else 0

        # Calcular margen con el coste real proyectado
        margen = (precio_mensual_eur - coste_proyectado) / precio_mensual_eur * 100

        # Determinar acción recomendada
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
