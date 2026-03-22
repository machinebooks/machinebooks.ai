# Extraído de: LibroFinOps/cap-06-atribucion.md
# services/budget_check.py
import redis.asyncio as aioredis
from sqlalchemy import select, func, and_
from datetime import datetime, timezone
from calendar import monthrange
from typing import Optional
from ..models import LLMUsageLog, BudgetConfig, UserBudgetOverride
from ..database import get_async_session

class BudgetCheckService:
    """
    Verifica el presupuesto disponible antes de ejecutar una llamada LLM.
    Usa Redis como caché de contadores para enforcement en tiempo real.
    Si Redis no está disponible, consulta MySQL directamente.
    """

    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client

    async def get_monthly_spend(self, scope: str, scope_id: Optional[str]) -> float:
        """
        Devuelve el gasto acumulado del mes actual para el scope dado.
        Intenta Redis primero; cae a MySQL si Redis no está disponible.
        """
        cache_key = f"budget:{scope}:{scope_id or 'global'}:{self._current_month_key()}"

        try:
            cached = await self._redis.get(cache_key)
            if cached is not None:
                return float(cached)
        except Exception:
            pass  # Redis no disponible: caemos a MySQL

        # Fallback a MySQL
        return await self._spend_from_mysql(scope, scope_id)

    async def _spend_from_mysql(self, scope: str, scope_id: Optional[str]) -> float:
        """Consulta el gasto del mes actual directamente en MySQL."""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        filters = [LLMUsageLog.timestamp >= month_start]
        if scope == "user" and scope_id:
            filters.append(LLMUsageLog.user_id == scope_id)
        elif scope == "service" and scope_id:
            filters.append(LLMUsageLog.service_name == scope_id)

        async with get_async_session() as session:
            result = await session.execute(
                select(func.coalesce(func.sum(LLMUsageLog.total_cost_usd), 0.0))
                .where(and_(*filters))
            )
            return float(result.scalar())

    async def check_budget(
        self,
        user_id: Optional[str],
        service_name: str,
        estimated_cost_usd: float = 0.0,
    ) -> dict:
        """
        Verifica si el usuario y el servicio tienen presupuesto disponible.
        Devuelve el estado del presupuesto y si la llamada está permitida.
        """
        result = {"allowed": True, "warnings": [], "blocks": []}

        # Cargar configuraciones de presupuesto activas
        budgets = await self._load_budgets(user_id, service_name)

        for budget in budgets:
            scope_label = f"{budget.scope}/{budget.scope_id or 'global'}"
            spend = await self.get_monthly_spend(budget.scope, budget.scope_id)
            limit = budget.budget_usd
            projected = spend + estimated_cost_usd
            ratio = projected / limit if limit > 0 else 0

            if ratio >= budget.block_threshold:
                result["allowed"] = False
                result["blocks"].append({
                    "scope": scope_label,
                    "spend_usd": round(spend, 4),
                    "limit_usd": limit,
                    "ratio": round(ratio, 3),
                    "message": f"Presupuesto agotado para {scope_label} ({ratio*100:.1f}%)",
                })
            elif ratio >= budget.alert_threshold:
                result["warnings"].append({
                    "scope": scope_label,
                    "spend_usd": round(spend, 4),
                    "limit_usd": limit,
                    "ratio": round(ratio, 3),
                    "message": f"Presupuesto al {ratio*100:.1f}% para {scope_label}",
                })

        return result

    async def _load_budgets(
        self, user_id: Optional[str], service_name: str
    ) -> list[BudgetConfig]:
        """
        Carga los presupuestos aplicables: global + por servicio + por usuario.
        El UserBudgetOverride tiene prioridad sobre BudgetConfig genérico de usuario.
        """
        async with get_async_session() as session:
            # Presupuesto global
            global_q = await session.execute(
                select(BudgetConfig).where(
                    and_(BudgetConfig.scope == "global", BudgetConfig.is_active == True)
                )
            )
            budgets = list(global_q.scalars().all())

            # Presupuesto del servicio
            svc_q = await session.execute(
                select(BudgetConfig).where(
                    and_(
                        BudgetConfig.scope == "service",
                        BudgetConfig.scope_id == service_name,
                        BudgetConfig.is_active == True,
                    )
                )
            )
            budgets.extend(svc_q.scalars().all())

            # Presupuesto del usuario: override tiene prioridad
            if user_id:
                override_q = await session.execute(
                    select(UserBudgetOverride).where(
                        and_(
                            UserBudgetOverride.user_id == user_id,
                            UserBudgetOverride.is_active == True,
                        )
                    )
                )
                override = override_q.scalar_one_or_none()

                if override:
                    # Crear un BudgetConfig sintético desde el override
                    synthetic = BudgetConfig(
                        scope="user",
                        scope_id=user_id,
                        budget_usd=override.budget_usd,
                        alert_threshold=0.80,
                        block_threshold=1.00,
                    )
                    budgets.append(synthetic)
                else:
                    # Buscar el BudgetConfig genérico de usuario
                    user_q = await session.execute(
                        select(BudgetConfig).where(
                            and_(
                                BudgetConfig.scope == "user",
                                BudgetConfig.scope_id == None,  # el genérico
                                BudgetConfig.is_active == True,
                            )
                        )
                    )
                    budgets.extend(user_q.scalars().all())

        return budgets

    def _current_month_key(self) -> str:
        now = datetime.now(timezone.utc)
        return f"{now.year}-{now.month:02d}"
