# Source: The FinOps Engineer and the Machine -- Chapter 11
# Pattern: BudgetConfig model (full version)

# models/budget_config.py
from sqlalchemy import Column, String, Float, Integer, Enum, DateTime, Boolean
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class BudgetScope(str, enum.Enum):
    """Scope of a budget: global, per service, or per user."""
    GLOBAL  = "global"
    SERVICE = "service"
    USER    = "user"

class BudgetPeriod(str, enum.Enum):
    """Budget renewal period."""
    DAILY   = "daily"
    WEEKLY  = "weekly"
    MONTHLY = "monthly"

class BudgetConfig(Base):
    """Budget configuration with three response levels."""
    __tablename__ = "budget_config"

    id             = Column(Integer, primary_key=True)
    name           = Column(String(100), unique=True)  # human-readable identifier
    scope          = Column(Enum(BudgetScope))
    scope_id       = Column(String(100), nullable=True)  # service or user_id
    period         = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    # Maximum limit in USD for the period
    limit_usd      = Column(Float)
    # Activation thresholds for each level (fraction of limit)
    alert_threshold    = Column(Float, default=0.80)  # 80%
    throttle_threshold = Column(Float, default=0.95)  # 95%
    block_threshold    = Column(Float, default=1.00)  # 100%
    # Current state (updated by the enforcement middleware)
    current_spend_usd  = Column(Float, default=0.0)
    period_start       = Column(DateTime)
    is_active          = Column(Boolean, default=True)
    updated_at         = Column(DateTime)
