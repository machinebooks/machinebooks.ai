# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: Statistical forecasting (triple exponential smoothing)

# forecasting/statistical_engine.py
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from models.cloud_cost_metric import CloudCostMetric
from sqlalchemy.orm import Session


class StatisticalForecaster:
    """
    Forecasting engine based on exponential moving average
    with seasonal adjustment. Deterministic and auditable.
    """

    def __init__(self, db: Session, provider: str = 'all'):
        self.db = db
        self.provider = provider

    def forecast_current_month(self) -> dict:
        """
        Projects current month spend using:
        1. Spending pace of elapsed days
        2. 90-day trend (EWMA)
        3. Seasonality factor for the current month
        """
        today = date.today()
        days_elapsed = today.day
        days_in_month = (
            date(today.year, today.month + 1, 1)
            - date(today.year, today.month, 1)
        ).days
        days_remaining = days_in_month - days_elapsed

        # Accumulated spend so far this month
        month_start = datetime(today.year, today.month, 1)
        current_cost = self._get_total_cost(
            month_start, datetime.utcnow()
        )

        # Simple projection: current daily rate * remaining days
        daily_rate = current_cost / days_elapsed if days_elapsed > 0 else 0
        simple_projection = current_cost + (daily_rate * days_remaining)

        # EWMA trend over the last 6 months
        trend = self._calculate_ewma_trend()

        # Seasonality factor from the previous year
        seasonality = self._calculate_seasonality(today.month)

        # Adjusted projection with trend and seasonality
        adjusted = simple_projection * seasonality * (1 + trend)

        return {
            'simple_projection_usd': round(simple_projection, 2),
            'trend_adjusted_projection_usd': round(adjusted, 2),
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'current_month_spend_usd': round(current_cost, 2),
            'daily_rate_usd': round(daily_rate, 2),
            'seasonality_factor': round(seasonality, 3),
            'trend_factor': round(trend, 3)
        }
