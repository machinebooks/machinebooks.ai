# Source: The FinOps Engineer and the Machine -- Chapter 17
# Pattern: HumanBaseline and ROIRecord models

# models/roi.py — Reference configuration and ROI recording
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class HumanBaselineConfig(Base):
    """
    Reference for calculating ROI per task type and role.
    Administered by the FinOps team, reviewed quarterly.
    """
    __tablename__ = "human_baseline_config"

    id = Column(Integer, primary_key=True)
    task_type = Column(String(100), nullable=False)       # e.g. "offer_generation"
    role = Column(String(50), nullable=False)             # e.g. "senior_consultant"
    human_minutes = Column(Float, nullable=False)         # reference human time
    hourly_cost_eur = Column(Float, nullable=False)       # role cost in EUR/hour
    supervision_overhead = Column(Float, default=0.10)    # supervision overhead
    productivity_capture = Column(Float, default=0.60)    # captured productivity factor
    is_bottleneck = Column(Boolean, default=False)        # capacity-limiting task?
    acceptance_rate = Column(Float, default=0.90)         # historical acceptance rate
    active = Column(Boolean, default=True)
    notes = Column(Text)                                  # assumptions and reviews
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    completions = relationship("TaskCompletionLog", back_populates="baseline_config")
