# Source: The FinOps Engineer and the Machine -- Chapter 18
# Pattern: Business case generator for CFO presentations

# services/business_case_generator.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from services.roi_tracker import ROITracker

@dataclass
class BusinessCaseScenario:
    name: str                          # "optimistic", "base", "conservative"
    productivity_capture_factor: float
    acceptance_rate_factor: float      # multiplier on real rate
    growth_rate_monthly: float         # monthly usage growth

@dataclass
class BusinessCaseSummary:
    generated_at: datetime
    period_days: int
    monthly_llm_cost_eur: float
    monthly_value_liberated_eur: float
    roi_adjusted: float
    engineering_investment_eur: float
    break_even_month: int
    year1_net_value_eur: float
    scenarios: List[dict] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
