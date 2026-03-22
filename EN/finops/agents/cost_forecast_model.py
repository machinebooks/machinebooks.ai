# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: CostForecast model

# models/cost_forecast.py
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime
from database import Base


class CostForecast(Base):
    """
    Stores generated forecasts for traceability and evaluation.
    Actual accuracy is calculated at month-end by comparing
    with the final invoice.
    """
    __tablename__ = "cost_forecasts"

    id = Column(Integer, primary_key=True)
    provider = Column(String(20), nullable=False)   # 'aws', 'azure', 'all'
    forecast_month = Column(String(7), nullable=False)  # 'YYYY-MM'
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Forecast components
    statistical_forecast_usd = Column(Float, nullable=False)
    adjusted_forecast_usd = Column(Float, nullable=False)
    forecast_range_low_usd = Column(Float, nullable=True)
    forecast_range_high_usd = Column(Float, nullable=True)

    # Context used for adjustment
    business_context_used = Column(String(2000), nullable=True)
    llm_explanation = Column(String(3000), nullable=True)

    # Post-evaluation (filled at month close)
    actual_cost_usd = Column(Float, nullable=True)
    forecast_error_pct = Column(Float, nullable=True)
