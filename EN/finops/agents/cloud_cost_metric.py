# Source: The FinOps Engineer and the Machine -- Chapter 13
# Pattern: CloudCostMetric model for time-series data

# models/cloud_cost_metric.py
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from datetime import datetime
from database import Base


class CloudCostMetric(Base):
    """
    Cost time series by service and provider.
    One row per service per hour.
    """
    __tablename__ = "cloud_cost_metrics"

    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)  # 'aws', 'azure', 'gcp'
    service = Column(String(100), nullable=False)   # 'EC2', 'S3', 'AzureVM'...
    region = Column(String(50), nullable=True)
    cost_usd = Column(Float, nullable=False)
    usage_quantity = Column(Float, nullable=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for time series queries
    __table_args__ = (
        Index('idx_provider_service_period', 'provider', 'service', 'period_start'),
        Index('idx_period_start', 'period_start'),
    )


class CostAnomaly(Base):
    """Record of detected anomalies for traceability and learning."""
    __tablename__ = "cost_anomalies"

    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)
    service = Column(String(100), nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    z_score = Column(Float, nullable=False)
    cost_usd = Column(Float, nullable=False)         # Current cost
    expected_cost_usd = Column(Float, nullable=False) # Historical mean
    pct_deviation = Column(Float, nullable=False)     # Percentage deviation
    urgency = Column(String(10), nullable=False)      # 'high', 'medium', 'low'
    llm_explanation = Column(String(2000), nullable=True)
    action_taken = Column(String(200), nullable=True)
    was_false_positive = Column(Integer, nullable=True)  # 1=yes, 0=no
