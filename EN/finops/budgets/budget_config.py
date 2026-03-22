# Source: The FinOps Engineer and the Machine -- Chapter 6
# Pattern: BudgetConfig model with multi-level scopes

# models/budget_config.py
from sqlalchemy import Column, String, Float, Enum, DateTime, Boolean
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime, timezone
import uuid
from .base import Base

class BudgetConfig(Base):
    """
    Budget configuration by scope.
    A scope can be global, service, or user.
    """
    __tablename__ = "budget_configs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope = Column(
        Enum("global", "service", "user"),
        nullable=False,
        index=True,
    )
    scope_id = Column(String(128), nullable=True, index=True)
    # None for global; service_name for scope=service; user_id for scope=user

    period = Column(
        Enum("daily", "weekly", "monthly"),
        nullable=False,
        default="monthly",
    )

    budget_usd = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=0.80, nullable=False)   # alert at 80%
    block_threshold = Column(Float, default=1.00, nullable=False)   # block at 100%

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    notes = Column(String(512), nullable=True)   # override justification

    def __repr__(self):
        return f"<BudgetConfig scope={self.scope}/{self.scope_id} budget=${self.budget_usd}/mo>"


class UserBudgetOverride(Base):
    """
    Budget override for specific users.
    Replaces the generic scope=user BudgetConfig for that user_id.
    Requires justification and review date.
    """
    __tablename__ = "user_budget_overrides"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=False, unique=True, index=True)
    budget_usd = Column(Float, nullable=False)         # user's monthly limit
    justification = Column(String(512), nullable=False) # why the override
    review_date = Column(DateTime(timezone=True), nullable=False)  # when to review
    approved_by = Column(String(64), nullable=False)   # who approved
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
