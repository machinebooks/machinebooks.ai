# Extraído de: LibroFinOps/cap-11-presupuestos-circuit-breakers.md
# middleware/budget_enforcement.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.budget_config import BudgetConfig, BudgetScope
import asyncio
import logging

logger = logging.getLogger(__name__)

class BudgetAction(str, Enum):
    """Acción a tomar según el estado del presupuesto."""
    ALLOW    = "allow"     # < 80%: proceder normalmente
    ALERT    = "alert"     # 80-95%: permitir pero notificar
    THROTTLE = "throttle"  # 95-100%: añadir delay de 2 segundos
    BLOCK    = "block"     # >=100%: rechazar la petición

@dataclass
class BudgetCheckResult:
    """Resultado de la comprobación de presupuesto."""
    action:       BudgetAction
    budget_name:  str
    current_usd:  float
    limit_usd:    float
    utilization:  float   # fracción consumida (0.0-1.0+)
    message:      str

class BudgetEnforcementMiddleware:
    """
    Middleware de enforcement de presupuestos.
    Se ejecuta ANTES de cada llamada LLM para decidir si procede.
    """

    THROTTLE_DELAY_SECONDS = 2.0

    def __init__(self, db: Session, notifier):
        self.db       = db
        self.notifier = notifier  # servicio de notificaciones (Slack, email)

    async def check_and_enforce(
        self,
        service_name: str,
        user_id: Optional[str],
        estimated_cost_usd: float,
    ) -> BudgetCheckResult:
        """
        Comprueba todos los presupuestos aplicables y devuelve la acción más restrictiva.
        Aplica throttle (con delay real) o lanza excepción si debe bloquear.
        """
        configs = self._get_applicable_configs(service_name, user_id)
        most_restrictive = BudgetCheckResult(
            action=BudgetAction.ALLOW,
            budget_name="none",
            current_usd=0, limit_usd=0, utilization=0,
            message="OK",
        )

        for config in configs:
            result = self._evaluate_config(config)

            # Actualizar el resultado si este presupuesto es más restrictivo
            if result.action.value > most_restrictive.action.value:
                most_restrictive = result

        # Ejecutar la acción determinada
        if most_restrictive.action == BudgetAction.BLOCK:
            self._send_alert(most_restrictive, level="critical")
            raise BudgetExceededException(
                f"Presupuesto '{most_restrictive.budget_name}' agotado. "
                f"Uso actual: ${most_restrictive.current_usd:.2f} / "
                f"${most_restrictive.limit_usd:.2f}"
            )

        elif most_restrictive.action == BudgetAction.THROTTLE:
            logger.warning("Budget throttle: %s", most_restrictive.budget_name)
            await asyncio.sleep(self.THROTTLE_DELAY_SECONDS)
            self._send_alert(most_restrictive, level="warning")

        elif most_restrictive.action == BudgetAction.ALERT:
            self._send_alert(most_restrictive, level="info")

        return most_restrictive

    def _evaluate_config(self, config: BudgetConfig) -> BudgetCheckResult:
        """Evalúa un presupuesto concreto y determina la acción."""
        utilization = config.current_spend_usd / config.limit_usd

        if utilization >= config.block_threshold:
            action = BudgetAction.BLOCK
        elif utilization >= config.throttle_threshold:
            action = BudgetAction.THROTTLE
        elif utilization >= config.alert_threshold:
            action = BudgetAction.ALERT
        else:
            action = BudgetAction.ALLOW

        return BudgetCheckResult(
            action=      action,
            budget_name= config.name,
            current_usd= config.current_spend_usd,
            limit_usd=   config.limit_usd,
            utilization= utilization,
            message=     f"{utilization*100:.1f}% del presupuesto consumido",
        )

    def record_spend(self, config_ids: list[int], cost_usd: float):
        """
        Actualiza el gasto acumulado en los presupuestos afectados.
        Se llama DESPUÉS de cada llamada LLM exitosa.
        """
        self.db.query(BudgetConfig).filter(
            BudgetConfig.id.in_(config_ids)
        ).update(
            {"current_spend_usd": BudgetConfig.current_spend_usd + cost_usd},
            synchronize_session=False,
        )
        self.db.commit()

    def _get_applicable_configs(
        self, service_name: str, user_id: Optional[str]
    ) -> list[BudgetConfig]:
        """Obtiene los presupuestos aplicables: global + servicio + usuario."""
        query = self.db.query(BudgetConfig).filter(
            BudgetConfig.is_active == True
        )
        configs = []

        # Presupuesto global
        configs += query.filter(BudgetConfig.scope == BudgetScope.GLOBAL).all()
        # Presupuesto del servicio
        configs += query.filter(
            BudgetConfig.scope == BudgetScope.SERVICE,
            BudgetConfig.scope_id == service_name,
        ).all()
        # Presupuesto del usuario
        if user_id:
            configs += query.filter(
                BudgetConfig.scope == BudgetScope.USER,
                BudgetConfig.scope_id == user_id,
            ).all()

        return configs

    def _send_alert(self, result: BudgetCheckResult, level: str):
        """Envía notificación al canal configurado (Slack, email)."""
        self.notifier.send(
            level=   level,
            title=   f"Budget {result.action.value}: {result.budget_name}",
            message= result.message,
            data=    {"usd": result.current_usd, "limit": result.limit_usd},
        )


class BudgetExceededException(Exception):
    """Excepción lanzada cuando un presupuesto está al 100 %."""
    pass
