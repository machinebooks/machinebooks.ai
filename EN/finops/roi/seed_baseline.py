# Source: The FinOps Engineer and the Machine -- Chapter 17
# Pattern: Initial HumanBaseline seed data

# models/roi.py — Record of each AI-completed task
class TaskCompletionLog(Base):
    """
    Unit record of completed task. ROI calculated on insert.
    """
    __tablename__ = "task_completion_log"

    id = Column(Integer, primary_key=True)
    baseline_config_id = Column(Integer, ForeignKey("human_baseline_config.id"))
    llm_usage_log_id = Column(Integer, ForeignKey("llm_usage_log.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    task_type = Column(String(100), nullable=False)
    accepted = Column(Boolean, default=True)           # did the user accept the output?
    llm_cost_eur = Column(Float, nullable=False)       # real token cost in EUR
    human_value_eur = Column(Float)                    # calculated freed value
    roi_gross = Column(Float)                          # gross ROI without corrections
    roi_adjusted = Column(Float)                       # ROI with overhead and capture factor
    completed_at = Column(DateTime, default=datetime.utcnow)
    context = Column(Text)                             # additional metadata (JSON)

    baseline_config = relationship("HumanBaselineConfig", back_populates="completions")
