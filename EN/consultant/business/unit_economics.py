# Source: The Consultant and the Machine -- Chapter 22
# Pattern: Unit economics: cost model, ROI tracker, decisions
from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class ConsultantProfile:
    """Economic profile of an individual consultant."""
    name: str
    annual_salary: float          # Gross annual salary
    loaded_cost: float            # Loaded cost (salary + SS + overhead)
    available_hours: int = 1760   # Available hours per year
    target_utilization: float = 0.75
    actual_utilization: float = 0.67
    avg_bill_rate: float = 105.0  # Average hourly rate

    @property
    def billable_hours(self) -> int:
        return int(self.available_hours * self.actual_utilization)

    @property
    def annual_revenue(self) -> float:
        return self.billable_hours * self.avg_bill_rate

    @property
    def gross_margin(self) -> float:
        return self.annual_revenue - self.loaded_cost

    @property
    def gross_margin_pct(self) -> float:
        return self.gross_margin / self.annual_revenue if self.annual_revenue > 0 else 0


@dataclass
class AIStackCost:
    """AI stack costs per consultant."""
    api_licenses_monthly: float = 100.0    # Claude API
    rag_infra_monthly: float = 30.0        # Qdrant + compute
    tools_monthly: float = 20.0            # Pandoc, CI, etc.
    first_year_training: float = 3200.0    # Training
    first_year_setup: float = 2800.0       # Initial setup

    @property
    def monthly_recurring(self) -> float:
        return self.api_licenses_monthly + self.rag_infra_monthly + self.tools_monthly

    @property
    def annual_recurring(self) -> float:
        return self.monthly_recurring * 12

    def total_year(self, year: int = 1) -> float:
        """Total cost for a given year."""
        base = self.annual_recurring
        if year == 1:
            base += self.first_year_training + self.first_year_setup
        return base

# --- Block 2 ---

@dataclass
class AugmentedEconomics:
    """Unit economics calculation engine for the augmented consultant."""
    baseline: ConsultantProfile
    ai_cost: AIStackCost
    compression_factor: float = 0.52    # ECF: 52% effort reduction
    price_retention: float = 0.80       # PAF: retains 80% of price
    capacity_conversion: float = 0.60   # IC: 60% of freed time becomes billable
    year: int = 1

    @property
    def hours_saved_per_project(self) -> float:
        """Hours saved per average project."""
        avg_project_hours = self.baseline.billable_hours / self._baseline_projects
        return avg_project_hours * self.compression_factor

    @property
    def _baseline_projects(self) -> float:
        """Estimated number of annual projects in traditional model."""
        avg_project_hours = 120  # Average hours per project
        return self.baseline.billable_hours / avg_project_hours

    @property
    def augmented_hours_per_project(self) -> float:
        """Hours required per project with AI."""
        return 120 * (1 - self.compression_factor)

    @property
    def augmented_projects(self) -> float:
        """Projects completed with augmented model."""
        freed_hours = self.baseline.billable_hours * self.compression_factor
        additional_billable = freed_hours * self.capacity_conversion
        total_hours = (self.baseline.billable_hours
                       - freed_hours + additional_billable + freed_hours)
        return total_hours / self.augmented_hours_per_project

    @property
    def augmented_revenue_per_project(self) -> float:
        """Revenue per project with augmented model."""
        baseline_revenue_per_project = 120 * self.baseline.avg_bill_rate
        return baseline_revenue_per_project * self.price_retention

    @property
    def augmented_annual_revenue(self) -> float:
        """Annual billing of the augmented consultant."""
        return self.augmented_projects * self.augmented_revenue_per_project

    @property
    def augmented_total_cost(self) -> float:
        """Total cost including AI."""
        return self.baseline.loaded_cost + self.ai_cost.total_year(self.year)

    @property
    def augmented_gross_margin(self) -> float:
        return self.augmented_annual_revenue - self.augmented_total_cost

    @property
    def augmented_margin_pct(self) -> float:
        if self.augmented_annual_revenue == 0:
            return 0
        return self.augmented_gross_margin / self.augmented_annual_revenue

    @property
    def roi_on_ai_investment(self) -> float:
        """ROI on the AI investment."""
        incremental_margin = self.augmented_gross_margin - self.baseline.gross_margin
        ai_investment = self.ai_cost.total_year(self.year)
        return incremental_margin / ai_investment if ai_investment > 0 else 0

    @property
    def breakeven_days(self) -> float:
        """Days to reach AI investment break-even."""
        daily_incremental = (
            (self.augmented_gross_margin - self.baseline.gross_margin) / 365
        )
        if daily_incremental <= 0:
            return float('inf')
        return self.ai_cost.total_year(self.year) / daily_incremental

# --- Block 3 ---

def generate_comparison_report(economics: AugmentedEconomics) -> dict:
    """Generates before/after comparative report."""
    baseline = economics.baseline
    report = {
        "consultant": baseline.name,
        "baseline": {
            "annual_revenue": round(baseline.annual_revenue, 2),
            "loaded_cost": baseline.loaded_cost,
            "gross_margin": round(baseline.gross_margin, 2),
            "gross_margin_pct": f"{baseline.gross_margin_pct:.1%}",
            "billable_hours": baseline.billable_hours,
            "estimated_projects": round(economics._baseline_projects, 1),
        },
        "augmented": {
            "annual_revenue": round(economics.augmented_annual_revenue, 2),
            "total_cost": round(economics.augmented_total_cost, 2),
            "ai_stack_cost": round(
                economics.ai_cost.total_year(economics.year), 2
            ),
            "gross_margin": round(economics.augmented_gross_margin, 2),
            "gross_margin_pct": f"{economics.augmented_margin_pct:.1%}",
            "estimated_projects": round(economics.augmented_projects, 1),
            "hours_per_project": round(
                economics.augmented_hours_per_project, 1
            ),
        },
        "delta": {
            "revenue_change": f"{(economics.augmented_annual_revenue / baseline.annual_revenue - 1):.1%}",
            "margin_change_pp": round(
                (economics.augmented_margin_pct - baseline.gross_margin_pct) * 100, 1
            ),
            "roi_on_ai": f"{economics.roi_on_ai_investment:.1f}x",
            "breakeven_days": round(economics.breakeven_days, 0),
        },
    }
    return report

# Usage example with scaled data
consultant = ConsultantProfile(
    name="Senior Consultant A",
    annual_salary=52_000,
    loaded_cost=68_000,
    avg_bill_rate=105.0,
    actual_utilization=0.67,
)

ai_costs = AIStackCost(
    api_licenses_monthly=100,
    rag_infra_monthly=30,
    tools_monthly=20,
    first_year_training=3_200,
    first_year_setup=2_800,
)

econ = AugmentedEconomics(
    baseline=consultant,
    ai_cost=ai_costs,
    compression_factor=0.52,
    price_retention=0.80,
    year=1,
)

report = generate_comparison_report(econ)
print(json.dumps(report, indent=2, ensure_ascii=False))

# --- Block 4 ---

from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ProjectRecord:
    """Record of a completed project."""
    project_id: str
    consultant: str
    project_type: str               # "audit", "assessment", "proposal", "advisory"
    client_sector: str
    # Baseline (without AI)
    baseline_hours: float            # Estimated hours without AI
    baseline_price: float            # Price that would have been charged without AI
    # Actual (with AI)
    actual_hours: float              # Actual hours invested
    actual_price: float              # Price charged
    ai_cost: float                   # Token + infra cost for this project
    # Metadata
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    satisfaction_score: Optional[int] = None  # 1-10 from client

    @property
    def hours_saved(self) -> float:
        return max(0, self.baseline_hours - self.actual_hours)

    @property
    def compression_actual(self) -> float:
        if self.baseline_hours == 0:
            return 0
        return self.hours_saved / self.baseline_hours

    @property
    def price_retention_actual(self) -> float:
        if self.baseline_price == 0:
            return 0
        return self.actual_price / self.baseline_price

    @property
    def incremental_margin(self) -> float:
        """Incremental margin attributable to AI."""
        cost_rate = 58  # Consultant cost/hour
        baseline_margin = self.baseline_price - (self.baseline_hours * cost_rate)
        actual_margin = (self.actual_price
                         - (self.actual_hours * cost_rate)
                         - self.ai_cost)
        return actual_margin - baseline_margin


@dataclass
class ROITracker:
    """Accumulates and analyzes AI ROI across the practice."""
    records: List[ProjectRecord] = field(default_factory=list)

    def add_project(self, record: ProjectRecord) -> None:
        self.records.append(record)

    @property
    def total_hours_saved(self) -> float:
        return sum(r.hours_saved for r in self.records)

    @property
    def total_incremental_margin(self) -> float:
        return sum(r.incremental_margin for r in self.records)

    @property
    def total_ai_cost(self) -> float:
        return sum(r.ai_cost for r in self.records)

    @property
    def aggregate_roi(self) -> float:
        if self.total_ai_cost == 0:
            return 0
        return self.total_incremental_margin / self.total_ai_cost

    @property
    def avg_compression(self) -> float:
        if not self.records:
            return 0
        return sum(r.compression_actual for r in self.records) / len(self.records)

    def by_project_type(self) -> dict:
        """ROI broken down by project type."""
        types: dict = {}
        for r in self.records:
            if r.project_type not in types:
                types[r.project_type] = []
            types[r.project_type].append(r)

        summary = {}
        for ptype, projects in types.items():
            total_ai = sum(p.ai_cost for p in projects)
            total_inc = sum(p.incremental_margin for p in projects)
            avg_comp = sum(p.compression_actual for p in projects) / len(projects)
            summary[ptype] = {
                "projects": len(projects),
                "avg_compression": f"{avg_comp:.0%}",
                "total_ai_cost": round(total_ai, 2),
                "total_incremental_margin": round(total_inc, 2),
                "roi": f"{total_inc / total_ai:.1f}x" if total_ai > 0 else "N/A",
            }
        return summary

# --- Block 5 ---

import anthropic

def generate_quarterly_analysis(tracker: ROITracker, quarter: str) -> str:
    """Generates quarterly ROI narrative analysis with Claude."""
    client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

    summary = {
        "quarter": quarter,
        "total_projects": len(tracker.records),
        "total_hours_saved": tracker.total_hours_saved,
        "aggregate_roi": f"{tracker.aggregate_roi:.1f}x",
        "avg_compression": f"{tracker.avg_compression:.0%}",
        "by_type": tracker.by_project_type(),
        "total_ai_investment": tracker.total_ai_cost,
        "total_incremental_margin": tracker.total_incremental_margin,
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""You are a financial analyst at a technology consulting practice.
Analyze the AI tools ROI data and generate an executive report. Include:
performance summary, trends by project type, alerts if any type has ROI
below 5x, and recommendations for the next quarter. Be direct, use data.""",
        messages=[{
            "role": "user",
            "content": (
                f"Quarter {quarter} data:\n"
                f"{json.dumps(summary, indent=2, ensure_ascii=False)}"
            )
        }]
    )
    return message.content[0].text
