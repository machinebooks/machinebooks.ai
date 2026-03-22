# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: Budget enforcement middleware

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
    """Action to take based on budget state."""
    ALLOW    = "allow"     # < 80%: proceed normally
    ALERT    = "alert"     # 80-95%: allow but notify
    THROTTLE = "throttle"  # 95-100%: add 2-second delay
    BLOCK    = "block"     # >=100%: reject the request

@dataclass
class BudgetCheckResult:
    """Result of the budget check."""
    action:       BudgetAction
    budget_name:  str
    current_usd:  float
    limit_usd:    float
    utilization:  float   # fraction consumed (0.0-1.0+)
    message:      str

class BudgetEnforcementMiddleware:
    """
    Budget enforcement middleware.
    Runs BEFORE each LLM call to decide whether to proceed.
    """

    THROTTLE_DELAY_SECONDS = 2.0

    def __init__(self, db: Session, notifier):
        self.db       = db
        self.notifier = notifier  # notification service (Slack, email)

    async def check_and_enforce(
        self,
        service_name: str,
        user_id: Optional[str],
        estimated_cost_usd: float,
    ) -> BudgetCheckResult:
        """
        Checks all applicable budgets and returns the most restrictive action.
        Applies throttle (with real delay) or raises exception if it should block.
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

            # Update result if this budget is more restrictive
            if result.action.value > most_restrictive.action.value:
                most_restrictive = result

        # Execute the determined action
        if most_restrictive.action == BudgetAction.BLOCK:
            self._send_alert(most_restrictive, level="critical")
            raise BudgetExceededException(
                f"Budget '{most_restrictive.budget_name}' exhausted. "
                f"Current usage: ${most_restrictive.current_usd:.2f} / "
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
        """Evaluates a specific budget and determines the action."""
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
            message=     f"{utilization*100:.1f}% of budget consumed",
        )

    def record_spend(self, config_ids: list[int], cost_usd: float):
        """
        Updates the accumulated spend in affected budgets.
        Called AFTER each successful LLM call.
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
        """Gets applicable budgets: global + service + user."""
        query = self.db.query(BudgetConfig).filter(
            BudgetConfig.is_active == True
        )
        configs = []

        # Global budget
        configs += query.filter(BudgetConfig.scope == BudgetScope.GLOBAL).all()
        # Service budget
        configs += query.filter(
            BudgetConfig.scope == BudgetScope.SERVICE,
            BudgetConfig.scope_id == service_name,
        ).all()
        # User budget
        if user_id:
            configs += query.filter(
                BudgetConfig.scope == BudgetScope.USER,
                BudgetConfig.scope_id == user_id,
            ).all()

        return configs

    def _send_alert(self, result: BudgetCheckResult, level: str):
        """Sends notification to the configured channel (Slack, email)."""
        self.notifier.send(
            level=   level,
            title=   f"Budget {result.action.value}: {result.budget_name}",
            message= result.message,
            data=    {"usd": result.current_usd, "limit": result.limit_usd},
        )


class BudgetExceededException(Exception):
    """Exception raised when a budget is at 100%."""
    pass
