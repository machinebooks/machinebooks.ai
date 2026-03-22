# Source: The FinOps Engineer and the Machine -- Chapter 17
# Pattern: ROITracker -- main calculation and period summary

# services/roi_tracker.py — Main calculation method
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from models.roi import HumanBaselineConfig, TaskCompletionLog

@dataclass
class ROIResult:
    task_type: str
    llm_cost_eur: float
    human_value_eur: float
    roi_gross: float          # (value - cost) / cost without corrections
    roi_adjusted: float       # with overhead and captured productivity
    productivity_captured_eur: float
    accepted: bool
    notes: str = ""

class ROITracker:
    """Calculates and records the ROI of each AI-completed task."""

    def __init__(self, db: Session):
        self.db = db

    def record_completion(
        self,
        task_type: str,
        llm_cost_eur: float,
        accepted: bool = True,
        role: str = "senior_consultant",
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        llm_usage_log_id: Optional[int] = None,
    ) -> Optional[ROIResult]:
        """Records a completed task and calculates its ROI."""
        config = self.db.query(HumanBaselineConfig).filter(
            HumanBaselineConfig.task_type == task_type,
            HumanBaselineConfig.role == role,
            HumanBaselineConfig.active == True,
        ).first()

        if not config:
            return None

        # Gross value: human time x role cost per minute
        human_value_gross = config.human_minutes * (config.hourly_cost_eur / 60)

        # Rejected task: cost is assumed, value is zero
        if not accepted:
            effective_value = 0.0
        else:
            # Correction 1: supervision overhead
            value_after_overhead = human_value_gross * (1.0 - config.supervision_overhead)
            # Correction 2: captured productivity factor
            capture = 0.90 if config.is_bottleneck else config.productivity_capture
            effective_value = value_after_overhead * capture

        # Gross and adjusted ROI calculation
        if llm_cost_eur > 0:
            roi_gross = (human_value_gross - llm_cost_eur) / llm_cost_eur
            roi_adjusted = (effective_value - llm_cost_eur) / llm_cost_eur
        else:
            roi_gross = roi_adjusted = 0.0

        # Persist the record
        log = TaskCompletionLog(
            baseline_config_id=config.id, llm_usage_log_id=llm_usage_log_id,
            user_id=user_id, tenant_id=tenant_id, task_type=task_type,
            accepted=accepted, llm_cost_eur=llm_cost_eur,
            human_value_eur=effective_value,
            roi_gross=roi_gross, roi_adjusted=roi_adjusted,
        )
        self.db.add(log)
        self.db.commit()

        return ROIResult(
            task_type=task_type, llm_cost_eur=llm_cost_eur,
            human_value_eur=effective_value, roi_gross=roi_gross,
            roi_adjusted=roi_adjusted, productivity_captured_eur=effective_value,
            accepted=accepted,
        )
