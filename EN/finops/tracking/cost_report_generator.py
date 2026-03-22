# Source: The FinOps Engineer and the Machine -- Chapter 3
# Pattern: TCO report data structures and generation

# cost_report_generator.py — TCO report data structures
# Each dataclass represents a layer of the cost map.

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class LLMCostSummary:
    """LLM call cost summary for a period."""
    period_start: str
    period_end: str
    total_calls: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost_eur: float = 0.0
    cost_by_model: dict = field(default_factory=dict)      # claude-sonnet-4-6, etc.
    cost_by_operation: dict = field(default_factory=dict)   # chat, analysis, generation
    cost_by_user_profile: dict = field(default_factory=dict)  # power, average, light

@dataclass
class CloudCostSummary:
    """Cloud cost summary by Docker service."""
    period_start: str
    period_end: str
    total_cost_eur: float = 0.0
    cost_by_service: dict = field(default_factory=dict)
    cost_compute: float = 0.0
    cost_storage: float = 0.0
    cost_network: float = 0.0

@dataclass
class TCOReport:
    """Complete TCO report for the period."""
    period_start: str
    period_end: str
    active_users: int = 0
    llm_cost: float = 0.0
    cloud_cost: float = 0.0
    people_cost: float = 0.0
    tools_cost: float = 0.0
    overhead_cost: float = 0.0
    total_tco: float = 0.0
    cost_per_user: float = 0.0
    cost_per_operation: dict = field(default_factory=dict)
    llm_detail: Optional[LLMCostSummary] = None
    cloud_detail: Optional[CloudCostSummary] = None
