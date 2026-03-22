# Source: The FinOps Engineer and the Machine -- Chapter 6
# Pattern: BudgetCounter model for real-time spend tracking

# models/budget_counter.py
from sqlalchemy import Column, String, Float, Integer, DateTime, Index
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime, timezone
import uuid
from .base import Base

class BudgetCounter(Base):
    """
    Accumulated spend counter by scope and period.
    Updated in write-through with each LLMUsageLog record.
    Enables O(1) queries in the enforcement middleware.
    """
    __tablename__ = "budget_counters"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope = Column(String(32), nullable=False)        # global / service / user / tenant
    scope_id = Column(String(128), nullable=True)     # None for global
    period_key = Column(String(10), nullable=False)   # YYYY-MM for monthly
    accumulated_usd = Column(Float, default=0.0, nullable=False)
    call_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("idx_counter_lookup", "scope", "scope_id", "period_key", unique=True),
    )
